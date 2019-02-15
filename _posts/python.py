import asyncio


async def print_after(message, delay):
    """Print a message after the specified delay (in seconds)"""
    await asyncio.sleep(delay)
    print(message)


async def main():

    # Start coroutine twice (hopefully they start!)
    first_awaitable = asyncio.ensure_future(print_after("world!", 2))
    second_awaitable = asyncio.ensure_future(print_after("Hello", 1))

    # Wait for coroutines to finish
    await first_awaitable
    await second_awaitable

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
