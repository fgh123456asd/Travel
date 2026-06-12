import axios from 'axios';
import store from "@/store";

export function request(config) {
  const instance = axios.create({
    baseURL: "http://127.0.0.1:8000",
    timeout: 5000,
  });

  // 请求拦截器：统一加 Token
  instance.interceptors.request.use(config => {
    const token = window.localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = "Bearer " + token;
    }
    return config;
  }, err => Promise.reject(err));

  // 响应拦截器：自动刷新 Token
  instance.interceptors.response.use(
    res => res.data || res,
    async err => {
      const originalRequest = err.config;

      // 如果是 403（Token过期）
      if (err.response?.status === 403 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          const refreshToken = localStorage.getItem("refresh_token");
          if (!refreshToken) throw new Error("无刷新Token");

          // 调用刷新接口
          const res = await axios.post(
            "http://127.0.0.1:8000/user/refresh-token",
            {},
            {
              headers: { Authorization: "Bearer " + refreshToken }
            }
          );

          const newAccessToken = res.data.access_token;
          localStorage.setItem("access_token", newAccessToken);

          // 重新请求
          originalRequest.headers.Authorization = "Bearer " + newAccessToken;
          return instance(originalRequest);
        } catch (e) {
          // 刷新失败 → 退出登录
          localStorage.clear();
          store.commit("setIsLogin", false);
          window.location.href = "/login";
          return Promise.reject(e);
        }
      }

      return Promise.reject(err);
    }
  );

  return instance(config);
}