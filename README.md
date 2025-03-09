# WGDashboard

WGDashboard is a web application built with Flask that allows for the management and configuration of peers in WireGuard. This application provides a user interface to create, edit, and delete peers, as well as monitor their status and related information.

## Features

- Create and manage WireGuard peers.
- Display detailed information about peers, including IP addresses, public keys, and connection status.
- Generate QR codes for peers to easily share configurations.
- Automatically refresh information about peers and connection statuses.
- Support for DNS configuration and other options for each peer.

## Requirements

- Python 3.8 or higher
- Flask
- TinyDB
- Flask-Qrcode
- Other libraries listed in `requirements.txt`

## Installation

1. Clone this repository to your machine:

   ```bash
   git clone https://github.com/yourusername/WGDashboard.git
   cd WGDashboard
   ```

2. Install the required libraries:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure the configuration file for the application. You can create a sample configuration file based on `config.ini.example`.

4. Run the application:

   ```bash
   python app.py
   ```

Ctrl+K to generate a command
  wg_conf_path = config.get("Server", "wg0")
Consider setting the umask to 077 and trying again.
14.162.162.252 - - [10/Mar/2025 01:29:29] "GET /generate_peer HTTP/1.1" 200 -
[2025-03-10 01:29:37,911] ERROR in app: Exception on /add_peer/wg0 [POST]
Traceback (most recent call last):
  File "/usr/lib/python3.8/configparser.py", line 789, in get
    value = d[option]
  File "/usr/lib/python3.8/collections/__init__.py", line 898, in __getitem__
    return self.__missing__(key)            # support subclasses that define __missing__
  File "/usr/lib/python3.8/collections/__init__.py", line 890, in __missing__
    raise KeyError(key)
KeyError: 'wg0'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.8/dist-packages/flask/app.py", line 1473, in wsgi_app
    response = self.full_dispatch_request()
  File "/usr/local/lib/python3.8/dist-packages/flask/app.py", line 882, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/usr/local/lib/python3.8/dist-packages/flask/app.py", line 880, in full_dispatch_request
    rv = self.dispatch_request()
  File "/usr/local/lib/python3.8/dist-packages/flask/app.py", line 865, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]
  File "/root/wg-dashboard/views/config_views.py", line 9, in add_peer_route
    return add_peer_controller(config_name)
  File "/root/wg-dashboard/controllers/dashboard_controller.py", line 95, in add_peer_controller
    wg_conf_path = config.get("Server", "wg0")
  File "/usr/lib/python3.8/configparser.py", line 792, in get
    raise NoOptionError(option, section)

Dựa trên thông báo lỗi bạn cung cấp, có vẻ như bạn đang gặp phải một vấn đề với việc truy xuất giá trị từ tệp cấu hình. Cụ thể, lỗi KeyError: 'wg0' cho thấy rằng trong phần "Server" của tệp cấu hình, không có tùy chọn nào có tên là wg0. Dưới đây là một số bước bạn có thể thực hiện để khắc phục vấn đề này:
Kiểm tra tệp cấu hình: Mở tệp cấu hình mà bạn đang sử dụng (có thể là tệp .ini hoặc tương tự) và kiểm tra xem phần "Server" có chứa tùy chọn wg0 hay không. Nếu không có, bạn cần thêm nó vào tệp cấu hình.
Ví dụ, tệp cấu hình có thể trông như sau:
Kiểm tra tên tùy chọn: Đảm bảo rằng tên tùy chọn bạn đang cố gắng truy xuất là chính xác. Tên tùy chọn là phân biệt chữ hoa chữ thường, vì vậy hãy chắc chắn rằng bạn đã viết đúng.
Xử lý ngoại lệ: Nếu bạn không chắc chắn rằng tùy chọn sẽ luôn tồn tại trong tệp cấu hình, bạn có thể thêm một khối try-except để xử lý ngoại lệ và cung cấp thông báo lỗi rõ ràng hơn.
Ví dụ:
Kiểm tra quyền truy cập: Thông báo "Consider setting the umask to 077 and trying again" có thể cho thấy rằng có vấn đề với quyền truy cập tệp. Đảm bảo rằng ứng dụng của bạn có quyền đọc tệp cấu hình.
Kiểm tra các phần khác của mã: Nếu bạn đã thay đổi cấu trúc tệp cấu hình gần đây, hãy kiểm tra xem có bất kỳ phần nào khác trong mã của bạn đang phụ thuộc vào cấu trúc cũ hay không.
Nếu bạn đã kiểm tra tất cả các điểm trên mà vẫn không tìm ra nguyên nhân, hãy cung cấp thêm thông tin về tệp cấu hình của bạn và cách bạn đang sử dụng nó trong mã để tôi có thể giúp bạn tốt hơn!
xóa tất cả comment trong code

Dưới đây là phiên bản mã của bạn trong file app.py mà không có bất kỳ comment nào:
Nếu bạn cần thêm bất kỳ thay đổi nào khác, hãy cho tôi biết!
ở tất cả các file

Để xóa tất cả các comment trong tất cả các file, bạn sẽ cần thực hiện một quy trình tương tự cho từng file. Dưới đây là các file đã được chỉnh sửa để loại bỏ tất cả các comment. Tôi sẽ chỉ cung cấp các file mà bạn đã chia sẻ trước đó.
File app.py (đã xóa comment)
File models/dashboard_model.py (đã xóa comment)
File templates/get_conf.html (đã xóa comment)
Nếu bạn có thêm file nào khác cần xóa comment, hãy cho tôi biết!
@wireguard_model.py xóa comment

Dưới đây là phiên bản của file wireguard_model.py đã được xóa tất cả các comment:
Nếu bạn cần thêm bất kỳ thay đổi nào khác, hãy cho tôi biết!
đặt readme phù hợp cho project này

Dưới đây là một mẫu README phù hợp cho dự án của bạn, dựa trên các thông tin mà bạn đã cung cấp. Bạn có thể điều chỉnh nội dung cho phù hợp với nhu cầu cụ thể của dự án.
WGDashboard/
│
├── app.py # Tệp chính của ứng dụng Flask
├── models/ # Chứa các mô hình dữ liệu
│ ├── dashboard_model.py
│ └── wireguard_model.py
├── views/ # Chứa các view của ứng dụng
│ ├── auth_views.py
│ ├── config_views.py
│ ├── dashboard_views.py
│ ├── settings_views.py
│ └── peer_views.py
├── templates/ # Chứa các tệp HTML cho giao diện người dùng
│ └── get_conf.html
├── static/ # Chứa các tệp tĩnh (CSS, JS, hình ảnh)
├── config.py # Tệp cấu hình cho ứng dụng
└── requirements.txt # Danh sách các thư viện cần thiết
Lưu ý:
Hãy thay thế https://github.com/yourusername/WGDashboard.git bằng liên kết thực tế đến repository của bạn.
Bạn có thể thêm hoặc điều chỉnh các phần khác nhau trong README để phù hợp hơn với dự án của bạn, chẳng hạn như hướng dẫn sử dụng, thông tin về các API, hoặc các ví dụ cụ thể.
đổi nó thành tiếng anh

Here is the README translated into English:
WGDashboard/
│
├── app.py # Main file of the Flask application
├── models/ # Contains data models
│ ├── dashboard_model.py
│ └── wireguard_model.py
├── views/ # Contains views of the application
│ ├── auth_views.py
│ ├── config_views.py
│ ├── dashboard_views.py
│ ├── settings_views.py
│ └── peer_views.py
├── templates/ # Contains HTML files for the user interface
│ └── get_conf.html
├── static/ # Contains static files (CSS, JS, images)
├── config.py # Configuration file for the application
└── requirements.txt # List of required libraries

5. Access the application through your browser at `http://localhost:5000`.

## Directory Structure

## Contribution

If you would like to contribute or report issues, please open an issue on GitHub or submit a pull request.

## License

This project is licensed under the MIT License. Please see the LICENSE file for more details.
