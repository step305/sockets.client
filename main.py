import socket
import time
import base64
import numpy as np
import cv2
import json

HOST, PORT = "192.168.136.131", 8008


def receive_packet(sock):
    chunk = ''
    data_list = []
    while '\r\n' not in chunk:
        chunk = sock.recv(1024).decode()
        data_list.append(chunk)
    data = ''.join(data_list)
    pack = json.loads(data)
    return pack, len(data)


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.settimeout(1)
    time.sleep(1)

    fps_t0 = time.monotonic()
    fps_cnt = 0

    speed_t0 = time.monotonic()
    speed_sz = 0

    s.send(b'Hello')
    packet, _ = receive_packet(s)
    buf_decode = base64.b64decode(packet['image'])
    timestamp0 = packet['timestamp']

    while True:
        try:
            s.send(b'get')
            packet, size_data = receive_packet(s)
            buf_decode = base64.b64decode(packet['image'])
            timestamp = (packet['timestamp'] - timestamp0) / 1e6

            speed_sz += size_data
            speed_t1 = time.monotonic()
            if speed_t1 - speed_t0 > 2:
                speed = speed_sz / (speed_t1 - speed_t0)
                speed_t0 = speed_t1
                print('Speed on data: {:0.1f}kbytes/sec on {:0.1f}kbytes of data'.format(speed / 1024, speed_sz / 1024))
                speed_sz = 0

            jpg = np.frombuffer(buf_decode, np.uint8)

            frame = cv2.imdecode(jpg, cv2.IMREAD_UNCHANGED)

            fps_cnt += 1
            fps_t1 = time.monotonic()
            if fps_t1 - fps_t0 > 2:
                fps = fps_cnt / (fps_t1 - fps_t0)
                fps_t0 = fps_t1
                print('Speed = {:0.1f}fps on {} frames'.format(fps, fps_cnt))
                fps_cnt = 0

            cv2.imshow('test', frame)
            if cv2.waitKey(1) == 27:
                break

            # print(str(s.recv(1000)))
        except KeyboardInterrupt:
            s.send(b'quit')
            s.recv(1000)
            # packet, _ = receive_packet(s)
            break
        except Exception:
            break
