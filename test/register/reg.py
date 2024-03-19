import aiohttp
import asyncio
import sys

async def upload_register(session, addr, user):
  payload = {'first_name': 'first_name_' + user, 'last_name': 'last_name_' + user,
             'username': 'username_' + user, 'password': 'password_' + user, 'user_id': user}
  # 向/wrk2-api/user/register发送请求,data为payload,返回resp 输出请求返回的代码
  async with session.post(addr + "/wrk2-api/user/register", data=payload) as resp:
    print(await resp.text())
    return await resp.text()


async def register(addr, nodes):
  idx = 0
  tasks = []
  conn = aiohttp.TCPConnector(limit=200)
  async with aiohttp.ClientSession(connector=conn) as session:
    for i in range(nodes, nodes + 1):
      task = asyncio.ensure_future(upload_register(session, addr, str(i)))
      tasks.append(task)
      idx += 1
      if idx % 200 == 0:
        resps = await asyncio.gather(*tasks)
        print("Registered", idx, "users successfully")
    resps = await asyncio.gather(*tasks)
    print("Registered", idx, "users successfully")


if __name__ == '__main__':
  if len(sys.argv) < 2:
    filename = "datasets/social-graph/socfb-Reed98/socfb-Reed98.mtx"
  else:
    filename = sys.argv[1]

  nodes = 10000

  addr = "http://localhost:30001"

  loop = asyncio.get_event_loop()
  future = asyncio.ensure_future(register(addr, nodes))
  loop.run_until_complete(future)
  # future = asyncio.ensure_future(follow(addr, edges))
  # loop.run_until_complete(future)
