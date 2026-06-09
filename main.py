import os
import time
import re
import unicodedata
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from supabase import create_client, Client

app = FastAPI(title="HUBT Cloud Storage Engine")

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://lhunflhmwyujwhrwclpp.supabase.co")
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
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; }
            .gradient-bg { background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); }
            .glass-card { background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(12px); }
        </style>
    </head>
    <body class="gradient-bg min-h-screen flex flex-col justify-between">

        <header class="bg-white/80 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-50">
            <div class="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between">
                <div class="flex items-center space-x-4">
                    <div class="bg-gradient-to-tr from-blue-600 to-indigo-600 text-white w-12 h-12 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/20">
                        <i class="fa-solid fa-cloud-arrow-up text-xl animate-pulse"></i>
                    </div>
                    <div>
                        <span class="text-xl font-extrabold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent block tracking-tight">HUBT Cloud Storage</span>
                        <span class="text-xs font-medium text-slate-400 block tracking-wide uppercase mt-0.5">Advanced Serverless Platform</span>
                    </div>
                </div>
                <div>
                    <span class="bg-emerald-50 text-emerald-700 text-xs px-3 py-1.5 rounded-xl font-semibold border border-emerald-200/60 flex items-center gap-2 shadow-sm">
                        <span class="w-2 h-2 bg-emerald-500 rounded-full animate-ping"></span>
                        <span class="w-2 h-2 bg-emerald-500 rounded-full absolute"></span>
                        Cloud Active Node
                    </span>
                </div>
            </div>
        </header>

        <main class="max-w-4xl mx-auto px-6 py-16 w-full flex-grow flex flex-col justify-center">
            <div class="text-center mb-12">
                <h1 class="text-4xl font-black text-slate-900 tracking-tight mb-4 sm:text-5xl leading-tight">
                    Hệ thống Phân phối & <br class="hidden sm:block"><span class="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">Lưu trữ Số hóa HUBT</span>
                </h1>
                <p class="text-slate-500 max-w-2xl mx-auto text-base leading-relaxed">
                    Trải nghiệm giải pháp sao lưu kiến trúc đám mây thế hệ mới. Toàn bộ tài liệu được mã hóa, tối ưu hóa băng thông truyền tải và đồng bộ hóa tức thì lên thực thể dữ liệu PostgreSQL.
                </p>
            </div>

            <div class="glass-card rounded-3xl shadow-2xl shadow-slate-200/80 border border-white p-8 sm:p-10 max-w-xl w-full mx-auto transition-all duration-300 hover:shadow-slate-300/70">
                <form id="uploadForm" enctype="multipart/form-data" class="space-y-6">
                    
                    <div id="dropZone" class="border-2 border-dashed border-slate-300/80 hover:border-blue-500 bg-slate-50/50 hover:bg-blue-50/30 rounded-2xl p-10 text-center cursor-pointer transition-all duration-300 group shadow-inner">
                        <input type="file" id="fileInput" name="document" class="hidden" required />
                        
                        <div class="space-y-4">
                            <div class="w-20 h-20 bg-white border border-slate-100 rounded-2xl shadow-md flex items-center justify-center mx-auto text-slate-400 group-hover:text-blue-600 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                                <i class="fa-solid fa-cloud-circle-arrow-up text-3xl"></i>
                            </div>
                            <div class="text-slate-600 text-sm sm:text-base">
                                <span class="font-bold text-blue-600 group-hover:text-blue-700 transition-colors">Bấm để duyệt tệp tin</span> hoặc kéo thả vùng này
                            </div>
                            <p class="text-xs font-medium text-slate-400/90 bg-slate-200/50 inline-block px-3 py-1 rounded-md">PDF, DOCX, PPTX, PNG, JPG, ZIP</p>
                        </div>
                    </div>

                    <div id="fileInfo" class="hidden bg-slate-900 text-white rounded-2xl p-4 flex items-center justify-between shadow-lg">
                        <div class="flex items-center space-x-3 overflow-hidden pr-2">
                            <div class="bg-blue-500/10 text-blue-400 w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 border border-blue-500/20">
                                <i class="fa-solid fa-file-invoice text-lg"></i>
                            </div>
                            <span id="fileName" class="text-sm font-semibold truncate tracking-wide">document.pdf</span>
                        </div>
                        <button type="button" id="removeFileBtn" class="w-8 h-8 rounded-lg bg-white/10 text-slate-300 hover:bg-rose-500 hover:text-white flex items-center justify-center transition-all duration-200">
                            <i class="fa-solid fa-trash-can text-xs"></i>
                        </button>
                    </div>

                    <button type="submit" id="submitBtn" class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-6 rounded-2xl shadow-lg shadow-blue-500/20 hover:shadow-xl hover:shadow-blue-500/30 active:scale-[0.99] transition-all duration-200 flex items-center justify-center space-x-3 group">
                        <i class="fa-solid fa-terminal text-sm opacity-60 group-hover:translate-x-0.5 transition-transform"></i>
                        <span>Khởi chạy Quy trình Lưu trữ</span>
                    </button>
                </form>

                <div id="resultBox" class="mt-8 hidden">
                    <div id="loadingStatus" class="hidden flex flex-col items-center justify-center py-6 space-y-3 bg-blue-50/40 rounded-2xl border border-blue-100">
                        <svg class="animate-spin h-9 w-9 text-blue-600" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span class="text-sm text-blue-800 font-semibold tracking-wide">Đang phân tách dữ liệu và ghi nhận đám mây...</span>
                    </div>

                    <div id="successStatus" class="hidden bg-emerald-50/80 border border-emerald-200 rounded-2xl p-6 space-y-4 shadow-sm">
                        <div class="flex items-center space-x-3 text-emerald-900 font-extrabold text-base">
                            <div class="bg-emerald-500 text-white w-8 h-8 rounded-full flex items-center justify-center shadow-md shadow-emerald-200">
                                <i class="fa-solid fa-check text-sm"></i>
                            </div>
                            <span>ĐỒNG BỘ DỮ LIỆU ĐÁM MÂY THÀNH CÔNG!</span>
                        </div>
                        <div class="text-xs text-slate-600 bg-white rounded-xl p-4 space-y-2 border border-slate-100 font-mono shadow-inner">
                            <div class="flex justify-between border-b border-slate-50 pb-1.5"><span class="font-sans text-slate-400 font-medium">Bản ghi hệ thống:</span> <span id="resName" class="font-bold text-slate-800"></span></div>
                            <div class="flex justify-between pt-0.5"><span class="font-sans text-slate-400 font-medium">Kích thước lưu trữ:</span> <span class="font-bold text-indigo-600"><span id="resSize"></span> KB</span></div>
                        </div>
                        <a id="resUrl" href="#" target="_blank" class="w-full bg-white hover:bg-slate-50 border border-slate-200 text-sm font-bold text-blue-600 py-3.5 px-4 rounded-xl flex items-center justify-center space-x-2 transition-all duration-150 active:scale-[0.99] shadow-sm">
                            <span>Truy xuất File trực tuyến (Object)</span>
                            <i class="fa-solid fa-arrow-up-right-from-square text-xs"></i>
                        </a>
                    </div>

                    <div id="errorStatus" class="hidden bg-rose-50 border border-rose-200 rounded-2xl p-5 flex items-start space-x-3 text-rose-900 shadow-sm">
                        <div class="bg-rose-500 text-white w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5 shadow-md shadow-rose-200">
                            <i class="fa-solid fa-triangle-exclamation text-xs"></i>
                        </div>
                        <div class="flex-grow">
                            <div class="font-extrabold tracking-tight">Hệ thống Đám mây Từ chối</div>
                            <p id="errorText" class="text-xs font-semibold text-rose-700 font-mono bg-white/60 p-3 rounded-xl mt-2 border border-rose-100 leading-relaxed"></p>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <footer class="bg-white border-t border-slate-200/60 py-6 text-center text-xs font-semibold text-slate-400 tracking-wider uppercase">
            Khoa Công nghệ thông tin - Đồ án cơ sở dữ liệu điện toán đám mây
        </footer>

        <script>
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
                    dropZone.classList.add('border-blue-500', 'bg-blue-50/30');
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    dropZone.classList.remove('border-blue-500', 'bg-blue-50/30');
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