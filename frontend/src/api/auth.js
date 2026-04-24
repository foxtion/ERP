import request from '@/utils/request'

/**
 * 认证相关 API
 */

export function login(data) {
  return request({
    url: '/system/auth/login/',
    method: 'post',
    data,
  })
}

export function logout() {
  return request({
    url: '/system/auth/logout/',
    method: 'post',
  })
}

export function getUserInfo() {
  return request({
    url: '/system/auth/info/',
    method: 'get',
  })
}

export function refreshToken(data) {
  return request({
    url: '/system/auth/refresh/',
    method: 'post',
    data,
  })
}

export function changePassword(data) {
  return request({
    url: '/system/auth/change-password/',
    method: 'post',
    data,
  })
}
