'use client';

import { useEffect, useRef, useCallback, useState } from 'react';

export function useWebSocket(
  url: string | null,
  onMessage: (data: any) => void
) {
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    if (!url) {
      setIsConnected(false);
      return;
    }

    let ws: WebSocket;
    let reconnectTimer: ReturnType<typeof setTimeout>;
    let closed = false;

    const connect = () => {
      ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => setIsConnected(true);

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessageRef.current(data);
        } catch { /* ignore */ }
      };

      ws.onclose = () => {
        setIsConnected(false);
        if (!closed) {
          reconnectTimer = setTimeout(connect, 2000);
        }
      };

      ws.onerror = () => ws.close();
    };

    connect();

    return () => {
      closed = true;
      clearTimeout(reconnectTimer);
      wsRef.current?.close();
      wsRef.current = null;
      setIsConnected(false);
    };
  }, [url]);

  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  return { isConnected, send };
}
