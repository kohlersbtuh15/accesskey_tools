**"accesskey_tools" Project Contains Malicious Dependency Risks**

The **"accesskey_tools"** project depends on the following four packages:

- "acloud-client"
- "credential-python-sdk"
- "enumer-iam"
- "tcloud-python-test"

These four packages are primarily used for credential management and permission testing in cloud services. However, all of them depend on a malicious package named "snapshot-photo". Although these four dependencies, as well as the "snapshot-photo" malicious package, have been removed from the official package repositories, they are still widely available on some third-party mirrors.

Malicious Behavior Analysis of "snapshot-photo":

- "snapshot-photo"
  - Obfuscated Malicious Requests:
    - Uses reversed strings (e.g., `self.endp[::-1]`) to hide the actual API endpoint, making it harder to detect.
    - The real URL is likely `https://api.aliyun-sdk-requests.xyz/{year}`, which appears to be related to Alibaba Cloud but may actually be a fake malicious server.
  - Data Exfiltration:
    - The `Dateformat` class collects data and sends it to a remote server via HTTP `POST` requests.
    - The server address is variable and appends the `year` as a path parameter, potentially used to categorize stored user data.
  - Exception Handling to Mask Behavior:
    - Uses `try-except` blocks that silently ignore all exceptions (`except: pass`), ensuring the malicious code runs quietly without raising errors.
    - This enables the code to run stealthily on the victim’s device without drawing attention.
  - Potential Remote Control Risk:
    - The server might return instructions to execute additional operations, such as downloading and running malicious scripts locally.
    - Combined with the use of `setup.py`’s `install_requires` or `entry_points`, this could lead to the automatic execution of malicious code during dependency installation.

Therefore, installing the **"accesskey_tools"** project from third-party mirrors may still lead to the download of versions containing malicious dependencies, posing significant security risks.

Below is an illustration of the process of reproducing the installation of the **"accesskey_tools"** project and encountering the malicious dependency attack:

![figure](https://github.com/user-attachments/assets/cca164b0-91a0-4972-bb76-425e008241c9)
