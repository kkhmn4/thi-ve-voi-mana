# Thi vẽ với Mana

Trò chơi vẽ cho học sinh lớp 4, 5. Em vẽ, Mana đoán và đọc dự đoán bằng tiếng Việt. Toàn bộ chạy trong trình duyệt, nét vẽ không gửi đi đâu, không cần tài khoản.

**Chơi thử:** https://thi-ve-voi-mana.netlify.app

## Luật chơi

- Vẽ 6 hình, mỗi hình 20 giây, 4 hình dễ và 2 hình thử thách. Chơi một mình hoặc đội 2 đến 3 bạn tiếp sức trên một máy: bạn nhận máy bấm Vẽ! thì giờ mới chạy.
- Đề chỉ có chữ, không có hình minh họa, để không lộ cách vẽ.
- Thắng một hình khi đủ ba điều, giữ được ở 2 lần đoán liền nhau: đề đứng đầu trong dự đoán của Mana, Mana chắc từ 30% trở lên, hình đủ nét. Đủ nét nghĩa là đạt số nét hoặc độ dài nét tối thiểu của chính đề đó, tính từ trung vị hình trong Quick, Draw!. Ví dụ con mèo: vòng tròn và 2 tai chưa thắng, thêm mắt hoặc ria mới thắng. Chưa đủ nét thì Mana nhắc vẽ thêm.
- Thắng thì có pháo giấy chúc mừng rồi sang hình kế. Hết 20 giây cũng sang hình kế.
- Có bút, gôm, xóa hết, bỏ qua.
- Cuối lượt, bấm vào từng hình để xem Mana đoán gì, mọi người vẽ thế nào, vì sao Mana đoán ra hoặc đoán nhầm.

Nút **Thử loa** ở màn đầu dùng để kiểm tra tiếng. Nên mở bằng Chrome hoặc Edge.

## Chạy không cần mạng

Tải tệp `thi-ve-voi-ai.html` về rồi bấm đúp để mở. Tệp đã gồm mô hình, giọng, hình, phông chữ.

## Dựng lại

Mã nguồn ở `nguon/`. Sửa `nguon/trang.html`, rồi chạy `python -X utf8 nguon/dong_goi.py <thư mục mô hình> <thư mục ndjson> 6`. Đầu tệp `dong_goi.py` ghi nơi lấy mô hình.

## Nguồn và giấy phép

| Thành phần | Nguồn | Giấy phép |
| --- | --- | --- |
| Mô hình đoán hình | DoodleNet của Yining Shi, ml5-data-and-models | MIT |
| Thư viện chạy mô hình | TensorFlow.js | Apache 2.0 |
| Hình mẫu | Quick, Draw! dataset, Google | CC BY 4.0 |
| Biểu tượng | Phosphor Icons | MIT |
| Phông chữ | Nunito | SIL OFL 1.1 |
| Giọng đọc | Sinh bằng VieNeu | Theo điều khoản của VieNeu |
| Nhân vật Mana | Chương trình giáo dục AI AISE | Không cấp phép dùng lại |
