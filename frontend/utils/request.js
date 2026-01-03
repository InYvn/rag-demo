// src/utils/request.js
import axios from 'axios';

// 本机测试请填: 'http://localhost:8000'
const BASE_URL = 'http://192.168.31.121:8000';

const service = axios.create({
  baseURL: BASE_URL,
  timeout: 10000     
});

service.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    console.error('请求出错:', error);
    return Promise.reject(error);
  }
);

export default service;