import ssl
import os
import random
import asyncio

# [중요] 맥(macOS) SSL 인증서 에러 방지 설정
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''

import flet as ft

async def main(page: ft.Page):
    # 앱 기본 설정
    page.title = "스포식스(Sportsix) 실시간 레이스"
    page.window_width = 400
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    GOAL_DIST = 3.0
    # 스포식스 크루 멤버 데이터
    runners = [
        {"name": "조광희(나)", "dist": 0, "speed": 0.012, "color": "blue"},
        {"name": "신짱구", "dist": 0, "speed": 0.015, "color": "green"},
        {"name": "나루토", "dist": 0, "speed": 0.013, "color": "orange"},
        {"name": "이슬이", "dist": 0, "speed": 0.011, "color": "red"},
    ]

    progress_bars = {}
    dist_texts = {}
    rank_texts = {}

    def create_runner_ui(name, color):
        pb = ft.ProgressBar(value=0, width=200, height=15, color=color, bgcolor="#eeeeee")
        dt = ft.Text("0.00km", size=14)
        rt = ft.Text("1위", size=16, weight="bold")
        
        ui_row = ft.Container(
            content=ft.Row([
                rt,
                ft.Column([
                    ft.Text(name, size=16, weight="w500"),
                    pb
                ], expand=True),
                dt
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=10,
            border=ft.Border.all(1, "#eeeeee"),
            border_radius=10
        )
        
        progress_bars[name] = pb
        dist_texts[name] = dt
        rank_texts[name] = rt
        return ui_row

    race_rows = ft.Column(spacing=10)
    for r in runners:
        race_rows.controls.append(create_runner_ui(r["name"], r["color"]))

    page.add(
        ft.Text("🏃‍♂️ 스포식스 실시간 레이스", size=26, weight="bold"),
        ft.Divider(height=20),
        race_rows
    )

    async def start_race(e):
        # 버튼을 누르면 안 보이게 숨김
        btn_start.visible = False
        page.update()
        
        while True:
            all_finished = True
            for r in runners:
                if r["dist"] < GOAL_DIST:
                    # 무작위 속도 및 부스터 로직
                    boost = 2.5 if random.random() < 0.05 else 1
                    r["dist"] += (r["speed"] + random.random() * 0.01) * boost
                    if r["dist"] >= GOAL_DIST: r["dist"] = GOAL_DIST
                    all_finished = False

            # 거리순 정렬하여 순위 실시간 업데이트
            ranked = sorted(runners, key=lambda x: x["dist"], reverse=True)
            for index, r in enumerate(ranked):
                name = r["name"]
                progress_bars[name].value = r["dist"] / GOAL_DIST
                dist_texts[name].value = f"{r['dist']:.2f}km"
                rank_texts[name].value = f"{index + 1}위"

            page.update()
            if all_finished: break
            await asyncio.sleep(0.1)

        page.open(ft.AlertDialog(title=ft.Text("레이스 종료!"), content=ft.Text("모두 고생하셨습니다.")))
        page.update()

    # ✨ 에러 해결: 제일 안전한 'content' 조립 방식으로 버튼 생성
    btn_start = ft.ElevatedButton(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.PLAY_ARROW),
                ft.Text("레이스 시작", size=16, weight="bold")
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True
        ),
        on_click=start_race,
        height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )
    
    page.add(
        ft.Divider(height=20, color="transparent"),
        ft.Row([btn_start], alignment=ft.MainAxisAlignment.CENTER)
    )

# 최신 flet 실행 방식
# 기존 코드의 마지막 부분을 아래처럼 변경
if __name__ == "__main__":
    import os
    # Render가 지정해주는 포트(PORT)를 사용하도록 설정
    port = int(os.getenv("PORT", 8000))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=port, host="0.0.0.0")