import os
import time
import re
import unicodedata
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from supabase import create_client, Client

app = FastAPI(title="HUBT Cloud Storage Engine")

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://dckgtjqroygumfgdulpb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "YOUR_SUPABASE_SECRET_KEY_HERE")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def secure_cloud_filename(filename: str) -> str:
    name_part, ext_part = os.path.splitext(filename)
    name_part = unicodedata.normalize('NFKD', name_part).encode('ascii', 'ignore').decode('utf-8')
    name_part = re.sub(r'[^a-zA-Z0-9._-]', '-', name_part)
    name_part = re.sub(r'-+', '-', name_part).strip('-')
    if not name_part:
        name_part = "unnamed-file"
    return f"{name_part}{ext_part.lower()}"

@app.get("/", response_class=HTMLResponse)
async def main_page():
    return """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HUBT Cloud Drive - Trung tâm Lưu trữ Tài liệu</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; }
            /* Custom Scrollbar */
            ::-webkit-scrollbar { width: 8px; }
            ::-webkit-scrollbar-track { background: transparent; }
            ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
            ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
            
            /* Background Blobs */
            .blob { position: absolute; filter: blur(90px); z-index: 0; opacity: 0.6; animation: float 10s infinite alternate; }
            .blob-1 { top: -10%; left: -10%; width: 500px; height: 500px; background: #93c5fd; }
            .blob-2 { bottom: -10%; right: -10%; width: 600px; height: 600px; background: #c4b5fd; animation-delay: -5s; }
            
            @keyframes float {
                0% { transform: translate(0, 0) scale(1); }
                100% { transform: translate(30px, 50px) scale(1.1); }
            }
        </style>
    </head>
    <body class="bg-slate-50 text-slate-800 min-h-screen flex flex-col justify-between relative overflow-x-hidden selection:bg-blue-500 selection:text-white">

        <div class="blob blob-1 pointer-events-none"></div>
        <div class="blob blob-2 pointer-events-none"></div>

        <header class="relative z-50 bg-white/60 backdrop-blur-xl border-b border-white/80 sticky top-0">
            <div class="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between">
                <div class="flex items-center space-x-4">
                    <div class="bg-gradient-to-br from-blue-600 to-indigo-700 text-white w-12 h-12 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30 ring-4 ring-white">
                        <i class="fa-solid fa-cloud-arrow-up text-xl"></i>
                    </div>
                    <div>
                        <span class="text-xl font-extrabold text-slate-900 block tracking-tight">HUBT<span class="text-blue-600">Cloud</span></span>
                        <span class="text-[11px] font-bold text-slate-500 block tracking-wider uppercase mt-0.5">Lưu trữ Serverless</span>
                    </div>
                </div>
                <div>
                    <div class="bg-white/80 backdrop-blur-sm border border-emerald-100 px-4 py-1.5 rounded-full flex items-center gap-2.5 shadow-sm">
                        <div class="relative flex h-2.5 w-2.5">
                          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                          <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                        </div>
                        <span class="text-xs font-bold text-emerald-700">System Online</span>
                    </div>
                </div>
            </div>
        </header>

        <main class="relative z-10 max-w-4xl mx-auto px-6 py-12 w-full flex-grow flex flex-col justify-center">
            
            <div class="text-center mb-12">
                <div class="inline-block mb-4 px-4 py-1.5 rounded-full bg-blue-50 border border-blue-100 text-blue-600 text-sm font-semibold tracking-wide shadow-sm">
                    ✨ Phiên bản 2.0 đã cập nhật
                </div>
                <h1 class="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight mb-5 leading-tight">
                    Nền tảng Lưu trữ & <br class="hidden sm:block">
                    <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600">Phân phối Số hóa HUBT</span>
                </h1>
                <p class="text-slate-500 max-w-xl mx-auto text-base leading-relaxed font-medium">
                    Giải pháp sao lưu đám mây thế hệ mới. Tài liệu được mã hóa, tối ưu băng thông và đồng bộ hóa tức thì với hạ tầng PostgreSQL.
                </p>
            </div>

            <div class="bg-white/70 backdrop-blur-2xl rounded-[2.5rem] shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white p-8 sm:p-12 max-w-xl w-full mx-auto transition-all duration-300 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)]">
                <form id="uploadForm" enctype="multipart/form-data" class="space-y-6">
                    
                    <div id="dropZone" class="relative overflow-hidden border-2 border-dashed border-slate-300 hover:border-blue-500 bg-slate-50/50 hover:bg-blue-50/30 rounded-[2rem] p-12 text-center cursor-pointer transition-all duration-300 group">
                        <input type="file" id="fileInput" name="document" class="hidden" required />
                        
                        <div class="relative z-10 flex flex-col items-center space-y-4">
                            <div class="w-20 h-20 bg-white rounded-full shadow-sm border border-slate-100 flex items-center justify-center text-slate-400 group-hover:text-blue-600 group-hover:scale-110 group-hover:shadow-md transition-all duration-500 ease-out">
                                <i class="fa-solid fa-arrow-up-from-bracket text-3xl transition-transform group-hover:-translate-y-1"></i>
                            </div>
                            <div>
                                <div class="text-slate-700 text-base font-medium mb-1">
                                    <span class="text-blue-600 font-bold group-hover:underline decoration-2 underline-offset-4">Chọn tệp</span> hoặc kéo thả vào đây
                                </div>
                                <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">PDF, DOCX, PPTX, PNG, JPG, ZIP</p>
                            </div>
                        </div>
                    </div>

                    <div id="fileInfo" class="hidden bg-slate-800 text-white rounded-2xl p-4 flex items-center justify-between shadow-lg transform transition-all">
                        <div class="flex items-center space-x-4 overflow-hidden pr-2">
                            <div class="bg-slate-700/50 text-blue-400 w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 border border-slate-600">
                                <i class="fa-solid fa-file-lines text-xl"></i>
                            </div>
                            <div class="flex flex-col">
                                <span class="text-xs text-slate-400 font-medium uppercase tracking-wider mb-0.5">Tệp đã chọn</span>
                                <span id="fileName" class="text-sm font-bold truncate max-w-[200px] sm:max-w-[250px]">document.pdf</span>
                            </div>
                        </div>
                        <button type="button" id="removeFileBtn" class="w-10 h-10 rounded-xl bg-slate-700 hover:bg-rose-500 text-slate-300 hover:text-white flex items-center justify-center transition-all duration-200">
                            <i class="fa-solid fa-xmark text-lg"></i>
                        </button>
                    </div>

                    <button type="submit" id="submitBtn" class="w-full relative overflow-hidden bg-slate-900 hover:bg-blue-600 text-white font-bold py-4 px-6 rounded-2xl shadow-lg hover:shadow-blue-500/25 active:scale-[0.98] transition-all duration-300 flex items-center justify-center space-x-3 group">
                        <i class="fa-solid fa-server text-sm opacity-70 group-hover:rotate-12 transition-transform duration-300"></i>
                        <span class="tracking-wide">Bắt đầu lưu trữ lên Cloud</span>
                    </button>
                </form>

                <div id="resultBox" class="mt-8 hidden">
                    
                    <div id="loadingStatus" class="hidden flex flex-col items-center justify-center py-8 space-y-4 bg-white/50 rounded-2xl">
                        <div class="relative w-12 h-12">
                            <div class="absolute inset-0 rounded-full border-4 border-slate-100"></div>
                            <div class="absolute inset-0 rounded-full border-4 border-blue-600 border-t-transparent animate-spin"></div>
                        </div>
                        <span class="text-sm text-slate-600 font-semibold tracking-wide animate-pulse">Đang đồng bộ hóa dữ liệu...</span>
                    </div>

                    <div id="successStatus" class="hidden animate-[fadeIn_0.3s_ease-out]">
                        <div class="bg-emerald-50 border border-emerald-100 rounded-2xl p-6 space-y-5">
                            <div class="flex items-center space-x-3">
                                <div class="bg-emerald-500 text-white w-10 h-10 rounded-full flex items-center justify-center shadow-md shadow-emerald-500/20 flex-shrink-0">
                                    <i class="fa-solid fa-check text-lg"></i>
                                </div>
                                <div>
                                    <h3 class="text-emerald-900 font-bold text-base leading-tight">Đồng bộ thành công!</h3>
                                    <p class="text-emerald-700/80 text-xs font-medium">Tệp đã được lưu an toàn trên Cloud</p>
                                </div>
                            </div>
                            
                            <div class="bg-white rounded-xl p-4 space-y-2.5 border border-emerald-50 shadow-sm">
                                <div class="flex justify-between items-center pb-2 border-b border-slate-100">
                                    <span class="text-slate-500 text-xs font-semibold">Tên bản ghi</span> 
                                    <span id="resName" class="font-bold text-slate-800 text-sm truncate max-w-[150px]"></span>
                                </div>
                                <div class="flex justify-between items-center pt-0.5">
                                    <span class="text-slate-500 text-xs font-semibold">Dung lượng</span> 
                                    <span class="font-bold text-blue-600 text-sm"><span id="resSize"></span> KB</span>
                                </div>
                            </div>
                            
                            <a id="resUrl" href="#" target="_blank" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-bold py-3.5 px-4 rounded-xl flex items-center justify-center space-x-2 transition-colors duration-200 shadow-sm">
                                <span>Truy cập File Online</span>
                                <i class="fa-solid fa-arrow-up-right-from-square text-xs opacity-80"></i>
                            </a>
                        </div>
                    </div>

                    <div id="errorStatus" class="hidden animate-[fadeIn_0.3s_ease-out]">
                        <div class="bg-rose-50 border border-rose-100 rounded-2xl p-6">
                            <div class="flex items-start space-x-3">
                                <div class="bg-rose-500 text-white w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md shadow-rose-500/20">
                                    <i class="fa-solid fa-triangle-exclamation text-lg"></i>
                                </div>
                                <div class="flex-grow pt-1">
                                    <h3 class="text-rose-900 font-bold text-base leading-tight mb-2">Đã xảy ra lỗi</h3>
                                    <p id="errorText" class="text-xs font-mono text-rose-700 bg-white p-3 rounded-lg border border-rose-100 break-words"></p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                </div>
            </div>
        </main>

        <footer class="relative z-10 py-6 text-center text-xs font-bold text-slate-400 tracking-widest uppercase">
            Khoa CNTT • Đồ án CSDL Điện toán Đám mây
        </footer>

        <script>
            // [Giữ nguyên toàn bộ logic JS cũ]
            const dropZone = document.getElementById('dropZone');
            const fileInput = document.getElementById('fileInput');
            const fileInfo = document.getElementById('fileInfo');
            const fileName = document.getElementById('fileName');
            const removeFileBtn = document.getElementById('removeFileBtn');
            const uploadForm = document.getElementById('uploadForm');
            const resultBox = document.getElementById('resultBox');
            const loadingStatus = document.getElementById('loadingStatus');
            const successStatus = document.getElementById('successStatus');
            const errorStatus = document.getElementById('errorStatus');

            dropZone.addEventListener('click', () => fileInput.click());

            ['dragenter', 'dragover'].forEach(eventName => {
                dropZone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    dropZone.classList.add('border-blue-500', 'bg-blue-50/50');
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    dropZone.classList.remove('border-blue-500', 'bg-blue-50/50');
                }, false);
            });

            dropZone.addEventListener('drop', (e) => {
                const dt = e.dataTransfer;
                const files = dt.files;
                if(files.length > 0) {
                    fileInput.files = files;
                    updateFileDisplay();
                }
            });

            fileInput.addEventListener('change', updateFileDisplay);

            function updateFileDisplay() {
                if(fileInput.files.length > 0) {
                    fileName.innerText = fileInput.files[0].name;
                    fileInfo.classList.remove('hidden');
                    dropZone.classList.add('hidden');
                }
            }

            removeFileBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                fileInput.value = '';
                fileInfo.classList.add('hidden');
                dropZone.classList.remove('hidden');
            });

            uploadForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                if(fileInput.files.length === 0) return;

                resultBox.classList.remove('hidden');
                loadingStatus.classList.remove('hidden');
                successStatus.classList.add('hidden');
                errorStatus.classList.add('hidden');

                const formData = new FormData();
                formData.append('document', fileInput.files[0]);

                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();
                    loadingStatus.classList.add('hidden');

                    if(response.ok) {
                        document.getElementById('resName').innerText = data.database_record.ten_tai_lieu;
                        document.getElementById('resSize').innerText = data.database_record.kich_thuoc;
                        document.getElementById('resUrl').href = data.cloud_storage_url;
                        successStatus.classList.remove('hidden');
                    } else {
                        document.getElementById('errorText').innerText = data.detail || 'Critical Server Exception.';
                        errorStatus.classList.remove('hidden');
                    }
                } catch (error) {
                    loadingStatus.classList.add('hidden');
                    document.getElementById('errorText').innerText = 'Network error: Connection to Cloud Web Server refused.';
                    errorStatus.classList.remove('hidden');
                }
            });
        </script>
    </body>
    </html>
    """

@app.post("/upload")
async def upload_file(document: UploadFile = File(...)):
    try:
        file_content = await document.read()
        
        safe_name = secure_cloud_filename(document.filename)
        unique_file_name = f"{int(time.time())}-{safe_name}"
        
        supabase.storage.from_("documents").upload(
            path=unique_file_name,
            file=file_content,
            file_options={"content-type": document.content_type}
        )
        
        public_url = str(supabase.storage.from_("documents").get_public_url(unique_file_name))
        file_size_kb = round(len(file_content) / 1024)

        db_response = supabase.table("tai_lieu").insert({
            "ten_tai_lieu": document.filename,
            "loai_file": document.content_type,
            "kich_thuoc": file_size_kb,
            "url_file": public_url
        }).execute()
        
        return {
            "message": "Success",
            "database_record": db_response.data[0],
            "cloud_storage_url": public_url
        }

    except Exception as e:
        print(f"Error Log: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database Serverless Refusal: {str(e)}")