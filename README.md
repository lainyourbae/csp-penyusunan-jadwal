# csp-penyusunan-jadwal
Input: template format json
Output: jadwal krs format csv
Tools: Z3, python
Constraints:
	- Setiap mahasiswa harus mengambil seluruh mata kuliah dan setiap mata kuliah hanya boleh diambil 1 paralel
	- Setiap mata kuliah yang diambil tidak boleh bertabrakan satu dengan yang lainnya
	- Setiap kelas harus seimbang jumlah mahasiswanya
Cara kerja agent:
	- Membuat daftar paralel mata kuliah yang bertabrakan
	- Representasikan CSP dengan symbolic variabel bertipe data boolean (Membuat sebanyak jumlah mahasiswa x jumlah matkul x jumlah paralel)
	- Membuat constraint dengan memberi aturan ke symbolic variabel tersebut
	- Dilanjutkan hingga didapatkan hasil oleh Z3
	- Hasil CSP nya dikonversi dari boolean ke csv
