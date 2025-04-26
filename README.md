五子棋 - Tkinter版 🎯

这是一个用 Python (Tkinter + Pygame + PIL) 开发的 ‘五子棋’ 应用。  
支持人机对战、双人对战、悔棋、音效、胜利记录保存等多种功能，界面美观，体验流畅！

✨ 功能特点

AI对战模式：与内置简单AI对弈。
双人对战模式：支持两位玩家同屏竞技。
悔棋功能：支持撤销上一步或AI步。
胜利记录保存：自动保存对局胜负记录（JSON文件）。
棋盘预览提示：鼠标悬停预览落子位置。
音效提示：每次落子有轻快的音效反馈（可开关）。
美化UI界面：自制棋子阴影、棋盘星位等视觉细节。

📦 依赖环境
- Python 3.7+
- Tkinter（Python标准库自带）
- Pygame
- Pillow (PIL)

安装所需库：

pip install pygame pillow

📸 界面截图
![image](https://github.com/user-attachments/assets/8a9a0b76-2c54-461e-8093-9ec285ac61b7)

📝 备注

音效文件需放在项目目录下，命名为 `music.wav`。若未提供，将自动忽略音效功能。
胜利记录文件为 `win_records.json`，首次运行时会自动生成。

📜 License

本项目使用 MIT License，欢迎自由学习、使用与修改！
