# Ploof

**Ploof** is a modern desktop torrent search app that lets you quickly search for torrents on 1337x and send magnet links directly to your Premiumize account—all from a sleek, dark-themed PyQt6 interface.

![Ploof Screenshot](icon.png)

---

## Features

- 🔍 **Search 1337x**: Instantly search torrents from 1337x.to.
- 📋 **View Results**: See torrent title, seeders, leechers, magnet link, and source URL.
- ⚡ **Send to Premiumize**: One-click to send selected magnet links to your Premiumize cloud.
- 🌓 **Dark Theme**: Stylish, comfortable dark UI.
- 📋 **Copy Magnet/URL**: Right-click to copy any cell.

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd ploof
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. **Run the app:**
   ```bash
   python main.py
   ```
2. **Enter your Premiumize API token** when prompted (first run only). You can find your token at [Premiumize.me API section](https://www.premiumize.me/account/#api).
3. **Search for torrents** using the search bar.
4. **Select a result** and click "Send to Premiumize" to transfer the torrent to your cloud.

---

## Configuration

- Your Premiumize API token is saved in `config.json` after the first prompt.
- To change the token, delete or edit `config.json`.

---

## Dependencies

- Python 3.8+
- PyQt6
- requests
- beautifulsoup4

Install all dependencies with `pip install -r requirements.txt`.

---

## Security & Disclaimer

- This app is for personal use. Respect your local laws regarding torrenting.
- Your Premiumize token is stored locally in plain text (`config.json`).

---

## Contributing

Pull requests and suggestions are welcome! Open an issue or submit a PR.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
