let serverUrl = 'http://localhost:8001'
let apiUrl = serverUrl

let axiosInstance = axios.create({
	baseURL:apiUrl,
	timeout: 1000,
	headers: {
		'Content-Type': 'application/x-www-form-urlencoded'
	}
})

axiosInstance.serverUrl = serverUrl
axiosInstance.apiUrl = apiUrl

axiosInstance.interceptors.request.use((config) => {
	config.headers.Authorization = localStorage.authorization
	return config;
})

axiosInstance.interceptors.response.use((response) => {
	let token = response.data.access_token
    // var token = response.headers.authorization
    if (token) {
	   localStorage.authorization = response.data.token_type  + " " + token
    }
    return response
})

export default axiosInstance