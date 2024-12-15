'''异步下载'''

import asyncio

import httpx
from tqdm import tqdm


HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
}
PROXIES = {
    'all://': 'socks5://127.0.0.1:10808/',
}


async def downloadWithBar(stream: httpx.Response, name: str, pos: int):
    '''下载流，给定进度条位置'''
    with tqdm(
        desc=name[-20:],
        total=int(stream.headers['content-length']),
        position=pos,
        leave=False, # 完成后清空该行
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar, open(name, 'wb') as f:
        async for chunk in stream.aiter_bytes(chunk_size=1024):
            bar.update(f.write(chunk))


class AsyncDownloader:
    '''下载方式为往队列里添加下载信息，下载协程从队列获取下载信息进行下载'''

    def __init__(
        self,
        ntask: int = 8,
        headers = HEADERS,
        proxies = PROXIES,
        follow_redirects = True,
        **kwargs,
    ):
        self.cli = httpx.AsyncClient(
            headers=headers,
            proxies=proxies,
            follow_redirects=follow_redirects,
            **kwargs,
        )
        # 下载队列，每次放入一个下载信息
        self.que = asyncio.Queue()
        # 每个下载协程占据一个进度条位置
        self.workers = [
            asyncio.create_task(self.worker(i)) for i in range(ntask)
        ]

    async def worker(self, pos: int):
        '''不断从队列中获取下载信息进行下载，可重写'''
        while True:
            info = await self.que.get()
            try:
                await self.download(pos, *info)
            finally:
                self.que.task_done()

    async def download(self, pos: int, url: str, name: str):
        '''默认的下载函数，下载失败则等待几秒重新下载'''
        while True:
            try:
                async with self.cli.stream('GET', url) as stream:
                    stream.raise_for_status()
                    await downloadWithBar(stream, name, pos)
                return
            except httpx.HTTPError as e:
                print(e)
                await asyncio.sleep(6)

    def add(self, url: str, name: str):
        '''默认的往队列里添加下载信息的函数'''
        self.que.put_nowait((url, name))

    async def aclose(self):
        await self.que.join()
        for worker in self.workers:
            worker.cancel()
        # return_exceptions 使 cancel 不抛出异常
        await asyncio.gather(*self.workers, return_exceptions=True)
        await self.cli.aclose()

    async def __aenter__(self):
        await self.cli.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()
