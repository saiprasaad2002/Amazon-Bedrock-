import asyncio
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import CosineStrategy
import base64

# Define a BrowserConfig to set the browser settings
browser_config = BrowserConfig(
    browser_type="chromium",
    headless=True,
    verbose=True
)

# Create a CrawlerRunConfig with the necessary configurations
# run_config = CrawlerRunConfig(
#     cache_mode=CacheMode.BYPASS,
#     extraction_strategy=CosineStrategy(
#         semantic_filter="generating video from text",
#         word_count_threshold=10,
#         sim_threshold=0.3,
#         linkage_method='ward'
#     )
# )

# async def media_handling():
#     async with AsyncWebCrawler() as crawler:
#         config = CrawlerRunConfig(
#             cache_mode=CacheMode.ENABLED,
#             exclude_external_images=False,
#             screenshot=True # Set this to True if you want to take a screenshot
#         )
#         result = await crawler.arun(
#             url="https://aws.amazon.com/ai/generative-ai/nova/",
#             config=config,
#         )
#         for img in result.media['images'][:5]:
#             print(f"Image URL: {img['src']}, Alt: {img['alt']}, Score: {img['score']}")

# content = asyncio.run(media_handling())
# print(content)



# async def extract_content(url: str):
#     async with AsyncWebCrawler(config=browser_config) as crawler:
#         try:
#             result = await crawler.arun(url=url, config=run_config)
#             if result.success:
#                 extracted_content = result.extracted_content
#                 if extracted_content:
#                     content = json.loads(extracted_content)
#                     return content
#                 else:
#                     raise ValueError("No content extracted from the URL.")
#             else:
#                 raise ValueError(f"Extraction failed: {result.error_message}")
#         except Exception as e:
#             print(f"An error occurred: {str(e)}")
#             return None

# url = "https://aws.amazon.com/ai/generative-ai/nova/"
# content = asyncio.run(extract_content(url))
# print(content)

async def media_handling():
    async with AsyncWebCrawler() as crawler:
        config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            exclude_external_images=False,
            # screenshot=True  # Set this to True to take a screenshot
        )
        result = await crawler.arun(
            url="https://aws.amazon.com/ai/generative-ai/nova/",
            config=config,
        )
        if result.screenshot:
            with open("screenshot.png", "wb") as f:
                f.write(base64.b64decode(result.screenshot))
            print("Screenshot saved as screenshot.png")
        
        for img in result.media['images'][:5]:
            print(f"Image URL: {img['src']}, Alt: {img['alt']}, Score: {img['score']}")

content = asyncio.run(media_handling())