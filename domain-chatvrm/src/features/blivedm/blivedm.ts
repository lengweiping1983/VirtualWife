// 获取当前环境变量，假设为PRODUCT_ENV
const environment = process.env.NODE_ENV;

// 定义基础URL
let baseUrl = "";
if (environment === "development") {
  // baseUrl = ":8000";
  baseUrl = "/api/chatbot";
} else if (environment === "production") {
  baseUrl = "/api/chatbot";
} else {
  throw new Error("未知环境变量");
}


export async function connect(): Promise<WebSocket> {
    const hostname = window.location.hostname;
    var port = window.location.port;
    if (!port) {
        // 默认端口，HTTP是80，HTTPS是443
        port = window.location.protocol === 'https:' ? '443' : '80';
    }
    const socket = new WebSocket(`ws://${hostname}:${port}/${baseUrl}/ws/`);
    socket.onopen = () => {
        console.log('WebSocket connection established.');
        socket.send('connection success');
    };
    socket.onclose = (event) => {
        console.log('WebSocket connection closed:', event);
        // 重新连接，每隔1秒尝试一次
        setTimeout(() => {
            console.log('Reconnecting...');
            connect(); // 重新调用connect()函数进行连接
        }, 1000);
    };
    return socket;
}
