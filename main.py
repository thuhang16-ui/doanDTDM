import os
import time
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from supabase import create_client, Client

app = FastAPI(title="Đồ án Cloud - Lưu trữ tài liệu")

# 1. CẤU HÌNH KẾT NỐI ĐÁM MÂY
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://lhunflhmwyujwhrwclpp.supabase.co")
# Sửa chính xác dòng 11 thành như thế này (Nhớ nhấn Ctrl + S để lưu lại):
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "YOUR_SUPABASE_SECRET_KEY_HERE")

# Khởi tạo Client kết nối Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Giao diện HTML Dashboard hiện đại sử dụng Tailwind CSS
@app.get("/", response_class=HTMLResponse)
async def main_page():
    return """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cloud Drive - Lưu trữ Tài liệu Sinh viên</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body class="bg-slate-50 min-h-screen font-sans flex flex-col justify-between">

        <header class="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
            <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <div class="bg-blue-600 text-white w-10 h-10 rounded-xl flex items-center justify-center shadow-md shadow-blue-200">
                        <i class="fa-solid fa-cloud-arrow-up text-lg"></i>
                    </div>
                    <div>
                        <span class="text-lg font-bold text-slate-800 block leading-tight">HUBT Cloud Storage</span>
                        <span class="text-xs text-slate-500 block">Hệ thống Lưu trữ & Chia sẻ Tài liệu Sinh viên</span>
                    </div>
                </div>
                <div class="flex items-center space-x-2">
                    <span class="bg-green-50 text-green-700 text-xs px-2.5 py-1 rounded-full font-medium border border-green-200 flex items-center gap-1">
                        <span class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span> Cloud Node Active
                    </span>
                </div>
            </div>
        </header>

        <main class="max-w-4xl mx-auto px-4 py-12 w-full flex-grow">
            <div class="text-center mb-10">
                <h1 class="text-3xl font-black text-slate-800 tracking-tight mb-3 sm:text-4xl">
                    Tải tài liệu lên Đám mây tốc độ cao
                </h1>
                <p class="text-slate-600 max-w-xl mx-auto text-sm sm:text-base">
                    Nền tảng lưu trữ Serverless kết hợp Object Storage giúp tối ưu tốc độ truyền tải, sao lưu dữ liệu an toàn và phân phối tệp tin tức thì.
                </p>
            </div>

            <div class="bg-white rounded-2xl shadow-xl border border-slate-100 p-6 sm:p-10 max-w-xl mx-auto">
                <form id="uploadForm" enctype="multipart/form-data" class="space-y-6">
                    
                    <div id="dropZone" class="border-2 border-dashed border-slate-300 hover:border-blue-500 bg-slate-50/50 hover:bg-blue-50/20 rounded-xl p-8 text-center cursor-pointer transition-all duration-200 group">
                        <input type="file" id="fileInput" name="document" class="hidden" required />
                        
                        <div class="space-y-3">
                            <div class="w-16 h-16 bg-white border border-slate-100 rounded-full shadow-sm flex items-center justify-center mx-auto text-slate-400 group-hover:text-blue-500 group-hover:scale-110 transition-transform duration-200">
                                <i class="fa-solid fa-folder-open text-2xl"></i>
                            </div>
                            <div class="text-slate-700">
                                <span class="font-semibold text-blue-600 group-hover:underline">Bấm để chọn tệp</span> hoặc kéo thả vào đây
                            </div>
                            <p class="text-xs text-slate-400">Hỗ trợ các định dạng PDF, DOCX, PPTX, PNG, JPG, ZIP...</p>
                        </div>
                    </div>

                    <div id="fileInfo" class="hidden bg-slate-50 border border-slate-200 rounded-lg p-3 flex items-center justify-between">
                        <div class="flex items-center space-x-3 overflow-hidden">
                            <i class="fa-solid fa-file-lines text-blue-500 text-xl flex-shrink-0"></i>
                            <span id="fileName" class="text-sm font-medium text-slate-700 truncate">name.pdf</span>
                        </div>
                        <button type="button" id="removeFileBtn" class="text-slate-400 hover:text-red-500 transition-colors">
                            <i class="fa-solid fa-xmark"></i>
                        </button>
                    </div>

                    <button type="submit" id="submitBtn" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-xl shadow-lg shadow-blue-200 hover:shadow-xl hover:shadow-blue-300 active:scale-[0.98] transition-all duration-150 flex items-center justify-center space-x-2">
                        <i class="fa-solid fa-cloud-arrow-up"></i>
                        <span>Tải lên hệ thống Cloud</span>
                    </button>
                </form>

                <div id="resultBox" class="mt-6 hidden transition-all duration-300">
                    <div id="loadingStatus" class="hidden flex flex-col items-center justify-center py-4 space-y-2">
                        <svg class="animate-spin h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span class="text-sm text-slate-500 font-medium">Đang đóng gói luồng và đồng bộ lên đám mây...</span>
                    </div>

                    <div id="successStatus" class="hidden bg-emerald-50 border border-emerald-200 rounded-xl p-4 space-y-3">
                        <div class="flex items-center space-x-2 text-emerald-800 font-bold">
                            <i class="fa-solid fa-circle-check text-xl text-emerald-500"></i>
                            <span>Tải tài liệu lên Cloud thành công!</span>
                        </div>
                        <div class="text-xs text-emerald-700 bg-white/60 p-3 rounded-lg space-y-1 font-mono">
                            <div><strong class="font-sans text-slate-700">Tên file ghi nhận:</strong> <span id="resName"></span></div>
                            <div><strong class="font-sans text-slate-700">Kích thước:</strong> <span id="resSize"></span> KB</div>
                        </div>
                        <a id="resUrl" href="#" target="_blank" class="inline-flex items-center space-x-1 text-sm font-semibold text-blue-600 hover:text-blue-700 hover:underline">
                            <span>Mở xem file trực tiếp trên Cloud Storage</span>
                            <i class="fa-solid fa-arrow-up-right-from-square text-xs"></i>
                        </a>
                    </div>

                    <div id="errorStatus" class="hidden bg-rose-50 border border-rose-200 rounded-xl p-4 flex items-start space-x-2 text-rose-800">
                        <i class="fa-solid fa-circle-exclamation text-xl text-rose-500 flex-shrink-0 mt-0.5"></i>
                        <div>
                            <div class="font-bold">Lỗi xử lý đám mây!</div>
                            <p id="errorText" class="text-sm text-rose-700 mt-1"></p>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <footer class="bg-white border-t border-slate-100 py-4 text-center text-xs text-slate-400">
            <div>Đồ án môn Điện toán đám mây</div>
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

            // Kích hoạt click vào DropZone để mở hộp thoại chọn tệp
            dropZone.addEventListener('click', () => fileInput.click());

            // Xử lý sự kiện kéo thả file (Drag & Drop)
            ['dragenter', 'dragover'].forEach(eventName => {
                dropZone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    dropZone.classList.add('border-blue-500', 'bg-blue-50/20');
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    dropZone.classList.remove('border-blue-500', 'bg-blue-50/20');
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

            // Khi người dùng chọn file từ file chooser truyền thống
            fileInput.addEventListener('change', updateFileDisplay);

            function updateFileDisplay() {
                if(fileInput.files.length > 0) {
                    fileName.innerText = fileInput.files[0].name;
                    fileInfo.classList.remove('hidden');
                    dropZone.classList.add('hidden');
                }
            }

            // Nút hủy xóa tệp vừa chọn
            removeFileBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                fileInput.value = '';
                fileInfo.classList.add('hidden');
                dropZone.classList.remove('hidden');
            });

            // Xử lý submit gửi API bất đồng bộ (AJAX) không reload trang
            uploadForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                if(fileInput.files.length === 0) return;

                // Reset & hiển thị khu vực kết quả trạng thái
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
                        // Hiển thị trạng thái thành công trực quan dữ liệu từ Cloud
                        document.getElementById('resName').innerText = data.database_record.ten_tai_lieu;
                        document.getElementById('resSize').innerText = data.database_record.kich_thuoc;
                        
                        const fileUrl = data.cloud_storage_url;
                        const resUrlElement = document.getElementById('resUrl');
                        resUrlElement.href = fileUrl;
                        
                        successStatus.classList.remove('hidden');
                    } else {
                        document.getElementById('errorText').innerText = data.detail || 'Có lỗi không xác định xảy ra.';
                        errorStatus.classList.remove('hidden');
                    }
                } catch (error) {
                    loadingStatus.classList.add('hidden');
                    document.getElementById('errorText').innerText = 'Không thể kết nối đến Cloud Web Server.';
                    errorStatus.classList.remove('hidden');
                }
            });
        </script>
    </body>
    </html>
    """

# 3. API xử lý Upload File thẳng lên Cloud Storage và lưu URL vào DB (GIỮ NGUYÊN LOGIC CỦA BẠN)
@app.post("/upload")
async def upload_file(document: UploadFile = File(...)):
    try:
        file_content = await document.read()
        unique_file_name = f"{int(time.time())}-{document.filename}"
        
        # LUỒNG 1: Đẩy file lên Cloud Storage
        supabase.storage.from_("documents").upload(
            path=unique_file_name,
            file=file_content,
            file_options={"content-type": document.content_type}
        )
        
        # Lấy Public URL thực tế dạng chuỗi String từ Supabase
        public_url = str(supabase.storage.from_("documents").get_public_url(unique_file_name))
        
        file_size_kb = round(len(file_content) / 1024)

        # LUỒNG 2: Ghi dữ liệu vào Database PostgreSQL
        db_response = supabase.table("tai_lieu").insert({
            "ten_tai_lieu": document.filename,
            "loai_file": document.content_type,
            "kich_thuoc": file_size_kb,
            "url_file": public_url
        }).execute()
        
        return {
            "message": "Tải tài liệu lên Cloud bằng Python thành công!",
            "database_record": db_response.data[0],
            "cloud_storage_url": public_url
        }

    except Exception as e:
        print(f"Lỗi hệ thống: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Hệ thống Cloud gặp lỗi: {str(e)}")