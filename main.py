import ssl
import os
import random
import asyncio

# [중요] 맥(macOS) 및 Render SSL 에러 방지 설정
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''

import flet as ft

async def main(page: ft.Page):
    # 1. 버핏서울 스타일 프리미엄 다크 테마 설정
    page.title = "SPORSIX | CREW RACE"
    page.window_width = 400
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.with_opacity(1, "#1A1D21") # 깊은 다크 그레이 배경
    page.padding = 30
    page.scroll = ft.ScrollMode.AUTO

    GOAL_DIST = 5.0 # 목표 거리를 5km로 증량
    runners_data = [
        {"name": "조광희 (나)", "dist": 0, "speed": 0.02, "color": ft.Colors.CYAN_Accent, "avatar": "K"},
        {"name": "신짱구", "dist": 0, "speed": 0.025, "color": ft.Colors.GREEN_Accent, "avatar": "S"},
        {"name": "나루토", "dist": 0, "speed": 0.022, "color": ft.Colors.YELLOW_Accent, "avatar": "N"},
        {"name": "이슬이", "dist": 0, "speed": 0.021, "color": ft.Colors.AMBER_Accent, "avatar": "L"},
    ]

    # UI 객체를 담을 딕셔너리
    progress_bars = {}
    dist_texts = {}
    rank_badges = {}
    booster_icons = {}

    # 2. 버핏서울 느낌의 카드 디자인 함수 (질감, 그림자, 색상)
    def create_runner_ui(runner):
        name = runner["name"]
        color = runner["color"]
        
        # 순위 배지
        rt = ft.Text("1", size=18, weight="bold", color="#111111")
        rank_badge = ft.Container(
            content=rt,
            width=35, height=35,
            border_radius=18,
            bgcolor=color, # 해당 크루원의 고유 색상
            alignment=ft.alignment.center,
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.3, color))
        )
        
        # 아바타 (이름 첫 글자)
        avatar = ft.CircleAvatar(
            content=ft.Text(runner["avatar"], size=16, weight="bold"),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            color=ft.Colors.WHITE
        )

        # 프로그레스 바 (더 굵게, 네온 빛)
        pb = ft.ProgressBar(
            value=0, 
            width=200, height=20, 
            color=color, # 네온 계열
            bgcolor=ft.Colors.with_opacity(0.1, color),
            border_radius=10
        )
        
        # 거리 텍스트
        dt = ft.Text(
            "0.00 km", 
            size=18, 
            weight="w600", 
            font_family="Consolas", # 고정폭 글꼴로 숫자jitter 방지
            color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE)
        )
        
        # 부스터 아이콘 (평소엔 안 보임)
        bi = ft.Icon(ft.Icons.LIGHTNING_BOLT_ROUNDED, color=ft.Colors.RED_Accent, size=24, visible=False)
        
        # 카드 디자인 (컨테이너)
        ui_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    rank_badge,
                    ft.Row([avatar, ft.Text(name, size=20, weight="bold", font_family="Pretendard")]),
                    bi
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=15),
                ft.Row([pb, dt], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=15)
            ], spacing=15),
            padding=ft.padding.all(20),
            margin=ft.margin.only(bottom=15),
            bgcolor="#22262B", # 카드 배경색
            border_radius=20,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
            shadow=ft.BoxShadow(
                spread_radius=1, blur_radius=20,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 10)
            )
        )
        
        progress_bars[name] = pb
        dist_texts[name] = dt
        rank_badges[name] = rt # Text 객체만 저장 (순위 업데이트)
        booster_icons[name] = bi
        return ui_card

    # 3. 헤더 디자인 (탭 느낌)
    header = ft.Container(
        content=ft.Row([
            ft.Text("크루 랭킹", size=32, weight="bold", font_family="Pretendard"),
            ft.Text("실시간", size=16, color=ft.Colors.GREEN_Accent)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.only(bottom=30)
    )

    race_rows = ft.Column(spacing=0)
    for r in runners_data:
        race_rows.controls.append(create_runner_ui(r))

    page.add(
        header,
        ft.Divider(height=1, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
        ft.Divider(height=20, color="transparent"),
        race_rows
    )

    async def start_race(e):
        btn_start.visible = False
        page.update()
        
        # 초기화
        for r in runners_data: r["dist"] = 0

        while True:
            all_finished = True
            for r in runners_data:
                if r["dist"] < GOAL_DIST:
                    # 부스터 로직
                    is_booster = random.random() < 0.05
                    boost = 3.0 if is_booster else 1.0
                    r["dist"] += (r["speed"] + random.random() * 0.005) * boost
                    if r["dist"] >= GOAL_DIST: r["dist"] = GOAL_DIST
                    all_finished = False
                    
                    # 부스터 시각 효과
                    booster_icons[r["name"]].visible = is_booster

            # 순위 실시간 계산 및 UI 업데이트
            ranked = sorted(runners_data, key=lambda x: x["dist"], reverse=True)
            for index, r in enumerate(ranked):
                name = r["name"]
                progress_bars[name].value = r["dist"] / GOAL_DIST
                dist_texts[name].value = f"{r['dist']:.2f} km"
                rank_badges[name].value = str(index + 1)

            page.update()
            if all_finished: break
            await asyncio.sleep(0.08) # 업데이트 주기 더 빠르게 (역동성 증가)

        # 레이스 종료 알림 (심플하게)
        page.open(ft.AlertDialog(title=ft.Text("레이스 종료! 🏆"), content=ft.Text("모두 대단한 레이스였습니다.")))
        btn_start.visible = True
        page.update()

    # 프리미엄한 시작 버튼 디자인
    btn_start = ft.ElevatedButton(
        content=ft.Container(
            content=ft.Text("GO! 크루 레이스 시작", size=18, weight="bold", color="#111111"),
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
            bgcolor=ft.Colors.CYAN_Accent,
            border_radius=30,
        ),
        on_click=start_race,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=30)),
        elevation=10,
    )
    
    page.add(
        ft.Divider(height=40, color="transparent"),
        ft.Row([btn_start], alignment=ft.MainAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    ft.run(target=main, port=port, host="0.0.0.0")
