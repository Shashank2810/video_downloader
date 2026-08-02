from downloader.ytdlp import YTDLPDownloader

url = "https://www.youtube.com/watch?v=e9ZupmL9BcM"

downloader = YTDLPDownloader()

file = downloader.download_best(url)

print(file)