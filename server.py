from flask import Flask, render_template, request, send_from_directory, url_for
import os
import yt_dlp

app = Flask(__name__)

# ========================== 參數 ==========================
BASE_SAVE_FOLDER = r'D:\youtube_downloads'
#FFMPEG_PATH = r'D:/工具檔案/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe'
SUPPORTED_FORMATS = ['mp4', 'mp3', 'm4a', 'flac', 'webm', 'mkv']

# ========================== 網頁路由 ==========================

@app.route('/', methods=['GET', 'POST'])
def index():
    log = ""
    download_link = ""
    if request.method == 'POST':
        url = request.form.get('url')
        fmt = request.form.get('format')

        if not url:
            log = "⚠️ 請輸入影片網址！"
        elif fmt not in SUPPORTED_FORMATS:
            log = f"⚠️ 不支援的格式：{fmt}"
        else:
            log, filename = download_youtube(url, fmt)
            if filename:
                download_link = url_for('download_file', download_format=fmt, filename=filename)

    return render_template('index.html', log=log, formats=SUPPORTED_FORMATS, download_link=download_link)

@app.route('/download/<download_format>/<filename>')
def download_file(download_format, filename):
    directory = os.path.join(BASE_SAVE_FOLDER, download_format)
    return send_from_directory(directory, filename, as_attachment=True)

# ========================== 下載函式 ==========================

def download_youtube(url, download_format):
    save_folder = os.path.join(BASE_SAVE_FOLDER, download_format)
    os.makedirs(save_folder, exist_ok=True)

    ydl_opts = {
        'outtmpl': os.path.join(save_folder, '%(title)s.%(ext)s'),
        #'ffmpeg_location': FFMPEG_PATH,
        'cookiefile': r'D:\工具檔案\my_flask_app\cookies.txt',  # ✅ 這行路徑指向你的 cookies.txt
    }

    if download_format == 'mp4':
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
            'postprocessor_args': ['-c:v', 'copy', '-c:a', 'aac'],
        })
    elif download_format == 'mkv':
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mkv',
            'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mkv'}],
            'postprocessor_args': ['-c:v', 'copy', '-c:a', 'aac'],
        })
    elif download_format == 'webm':
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'webm',
            'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'webm'}],
            'postprocessor_args': ['-c:v', 'copy', '-c:a', 'opus'],
        })
    elif download_format in ['mp3', 'm4a', 'flac']:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': download_format, 'preferredquality': '192'}],
        })

    logs = []
    filename = None
    class MyLogger:
        def debug(self, msg): pass
        def warning(self, msg): pass
        def error(self, msg): logs.append(f"⚠️ {msg}")
        def info(self, msg): logs.append(msg)

    ydl_opts['logger'] = MyLogger()

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', '未知標題')
            width = info.get('width', '?')
            height = info.get('height', '?')
            filename = f"{title}.{download_format}"

            logs.append("\n✅ 下載完成！")
            logs.append(f"🎬 標題：{title}")
            if download_format in ['mp4', 'mkv', 'webm']:
                logs.append(f"📐 解析度：{width}x{height}")
            logs.append(f"💾 檔案已儲存在伺服器！可下載👇")
    except Exception as e:
        logs.append(f"❌ 下載錯誤：{e}")

    return "\n".join(logs), filename

# ========================== 主程式 ==========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
