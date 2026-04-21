"""
钉钉开放平台工具模块
提供 access_token 获取、考勤数据同步等功能
"""
import requests
from datetime import datetime, timedelta
from django.utils import timezone

DINGTALK_API_BASE = "https://oapi.dingtalk.com"


def get_access_token(app_key, app_secret):
    """
    获取钉钉 access_token
    """
    url = f"{DINGTALK_API_BASE}/gettoken"
    params = {"appkey": app_key, "appsecret": app_secret}
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("errcode") == 0:
            return data.get("access_token"), data.get("expires_in", 7200)
        return None, f"钉钉错误: {data.get('errmsg')}"
    except Exception as e:
        return None, f"请求异常: {str(e)}"


def get_cached_access_token():
    """
    从数据库获取缓存的 access_token，如果过期则重新获取
    """
    from apps.hr.models import DingTalkConfig
    config = DingTalkConfig.objects.first()
    if not config:
        return None, "未配置钉钉应用"

    # 检查 token 是否有效（提前5分钟刷新）
    if config.access_token and config.token_expires_at:
        if timezone.now() < config.token_expires_at - timedelta(minutes=5):
            return config.access_token, None

    # 重新获取 token
    token, err = get_access_token(config.app_key, config.app_secret)
    if not token:
        return None, err

    config.access_token = token
    config.token_expires_at = timezone.now() + timedelta(seconds=7200)
    config.save()
    return token, None


def get_attendance_records(access_token, user_ids, start_date, end_date, offset=0, limit=50):
    """
    获取钉钉打卡结果
    :param access_token: 钉钉 access_token
    :param user_ids: 钉钉用户ID列表，最大50个
    :param start_date: 开始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :param offset: 分页偏移
    :param limit: 每页条数，最大50
    :return: (records列表, 是否有更多数据, 错误信息)
    """
    url = f"{DINGTALK_API_BASE}/attendance/list"
    params = {"access_token": access_token}
    payload = {
        "workDateFrom": f"{start_date} 00:00:00",
        "workDateTo": f"{end_date} 23:59:59",
        "userIdList": user_ids,
        "offset": offset,
        "limit": limit,
    }
    try:
        resp = requests.post(url, params=params, json=payload, timeout=30)
        data = resp.json()
        if data.get("errcode") == 0:
            records = data.get("recordresult", [])
            has_more = len(records) >= limit
            return records, has_more, None
        return [], False, f"钉钉错误: {data.get('errmsg')}"
    except Exception as e:
        return [], False, f"请求异常: {str(e)}"


def get_all_attendance_records(access_token, user_ids, start_date, end_date):
    """
    获取全部考勤记录（自动分页）
    """
    all_records = []
    offset = 0
    limit = 50
    while True:
        records, has_more, err = get_attendance_records(
            access_token, user_ids, start_date, end_date, offset, limit
        )
        if err:
            return all_records, err
        all_records.extend(records)
        if not has_more:
            break
        offset += limit
    return all_records, None


def time_result_to_status(time_result):
    """
    钉钉打卡结果映射到系统考勤状态
    """
    mapping = {
        "Normal": "normal",
        "Late": "late",
        "Early": "early",
        "SeriousLate": "absent",
        "Absenteeism": "absent",
        "NotSigned": "absent",
    }
    return mapping.get(time_result, "normal")


def sync_attendance_to_system(start_date, end_date):
    """
    将钉钉考勤数据同步到系统 Attendance 模型
    :param start_date: 开始日期 (YYYY-MM-DD)
    :param end_date: 结束日期 (YYYY-MM-DD)
    :return: (同步数量, 错误信息)
    """
    from apps.hr.models import Employee, Attendance
    from datetime import datetime

    token, err = get_cached_access_token()
    if not token:
        return 0, err

    # 获取所有绑定了钉钉账号的在职员工
    employees = Employee.objects.filter(
        dingtalk_user_id__isnull=False,
        status__in=["active", "probation"]
    )
    if not employees.exists():
        return 0, "没有绑定钉钉账号的员工"

    user_id_map = {emp.dingtalk_user_id: emp for emp in employees}
    user_ids = list(user_id_map.keys())

    # 分批获取（每批最多50个用户）
    all_records = []
    for i in range(0, len(user_ids), 50):
        batch_ids = user_ids[i:i + 50]
        records, err = get_all_attendance_records(token, batch_ids, start_date, end_date)
        if err:
            return 0, err
        all_records.extend(records)

    # 按 userId + workDate + checkType 聚合为每天的上/下班记录
    daily_records = {}
    for rec in all_records:
        user_id = rec.get("userId")
        raw_work_date = rec.get("workDate", "")
        # 兼容字符串和整数时间戳
        if isinstance(raw_work_date, int):
            work_date = datetime.fromtimestamp(raw_work_date / 1000).strftime("%Y-%m-%d")
        else:
            work_date = str(raw_work_date)[:10]  # 取前10位日期部分
        check_type = rec.get("checkType")  # OnDuty / OffDuty
        key = (user_id, work_date)
        if key not in daily_records:
            daily_records[key] = {
                "user_id": user_id,
                "date": work_date,
                "check_in": None,
                "check_out": None,
                "check_in_status": None,
                "check_out_status": None,
                "base_check_in": None,
                "base_check_out": None,
                "dingtalk_detail": {"records": []},
            }

        # userCheckTime 是毫秒时间戳（实际打卡时间）
        user_check_time = rec.get("userCheckTime")
        check_time = None
        if user_check_time:
            try:
                dt = datetime.fromtimestamp(int(user_check_time) / 1000)
                check_time = dt.strftime("%H:%M:%S")
            except (ValueError, TypeError):
                pass

        # baseCheckTime 是排班基准打卡时间（毫秒时间戳）
        base_check_time = rec.get("baseCheckTime")
        base_time = None
        if base_check_time:
            try:
                dt = datetime.fromtimestamp(int(base_check_time) / 1000)
                base_time = dt.strftime("%H:%M:%S")
            except (ValueError, TypeError):
                pass

        time_result = rec.get("timeResult", "Normal")
        if check_type == "OnDuty":
            daily_records[key]["check_in"] = check_time
            daily_records[key]["check_in_status"] = time_result
            daily_records[key]["base_check_in"] = base_time
        elif check_type == "OffDuty":
            daily_records[key]["check_out"] = check_time
            daily_records[key]["check_out_status"] = time_result
            daily_records[key]["base_check_out"] = base_time

        # 保存原始钉钉数据快照（用于详情展示）
        daily_records[key]["dingtalk_detail"]["records"].append({
            "checkType": check_type,
            "timeResult": time_result,
            "userCheckTime": user_check_time,
            "baseCheckTime": base_check_time,
            "locationResult": rec.get("locationResult"),
            "sourceType": rec.get("sourceType"),
            "recordId": rec.get("recordId"),
        })

    # 写入数据库
    sync_count = 0
    for key, rec in daily_records.items():
        user_id, work_date = key
        employee = user_id_map.get(user_id)
        if not employee:
            continue

        # 确定状态：优先取迟到，其次早退，默认正常
        status = "normal"
        if rec["check_in_status"] in ["Late", "SeriousLate", "Absenteeism"]:
            status = "late"
        elif rec["check_out_status"] in ["Early", "Absenteeism"]:
            status = "early"
        elif not rec["check_in"] and not rec["check_out"]:
            status = "absent"

        # 计算迟到/早退分钟数
        late_minutes = 0
        early_minutes = 0
        if rec["check_in"] and rec["base_check_in"] and status == "late":
            try:
                actual = datetime.strptime(rec["check_in"], "%H:%M:%S")
                planned = datetime.strptime(rec["base_check_in"], "%H:%M:%S")
                diff = int((actual - planned).total_seconds() / 60)
                if diff > 0:
                    late_minutes = diff
            except Exception:
                pass
        if rec["check_out"] and rec["base_check_out"] and status == "early":
            try:
                actual = datetime.strptime(rec["check_out"], "%H:%M:%S")
                planned = datetime.strptime(rec["base_check_out"], "%H:%M:%S")
                diff = int((planned - actual).total_seconds() / 60)
                if diff > 0:
                    early_minutes = diff
            except Exception:
                pass

        obj, created = Attendance.objects.update_or_create(
            employee=employee,
            date=work_date,
            defaults={
                "check_in": rec["check_in"],
                "check_out": rec["check_out"],
                "base_check_in": rec["base_check_in"],
                "base_check_out": rec["base_check_out"],
                "status": status,
                "late_minutes": late_minutes,
                "early_minutes": early_minutes,
                "remark": "钉钉同步",
                "dingtalk_detail": rec["dingtalk_detail"],
            }
        )
        sync_count += 1

    return sync_count, None


def test_connection(app_key, app_secret):
    """
    测试钉钉连接
    """
    token, err = get_access_token(app_key, app_secret)
    if token:
        return True, None
    return False, err
