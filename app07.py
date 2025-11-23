import streamlit as st

# --- 定数と設定 ---
MAX_MASU = 25
REWARD_DAYS = [3, 7, 14, 21, 25]
START_MASU = 1
GOAL_MASU = MAX_MASU

# --- 初期化（アプリ起動時に一度だけ動く） ---
# st.session_state に必要な変数が存在するかチェックし、なければ初期値を設定
if "current_day" not in st.session_state:
    st.session_state.current_day = 1  # 現在の日数（マス番号）
if "history" not in st.session_state:
    # 履歴: {日数: "達成" / "未達成" / "ゴール済"}
    st.session_state.history = {}
if "theme" not in st.session_state:
    st.session_state.theme = "読書を25日継続する！"
if "rewards" not in st.session_state:
    # ご褒美リスト: {日数: {name: "ご褒美名", checked: False}}
    st.session_state.rewards = {day: {"name": "", "checked": False} for day in REWARD_DAYS}
if "consecutive_success" not in st.session_state:
    st.session_state.consecutive_success = 0  # 連続達成日数
if "animation_type" not in st.session_state:
    st.session_state.animation_type = None  # None, "balloons", or "goal_celebration"
if "reward_checked_animation" not in st.session_state:  # NEW: チェックボックス用アニメーションフラグ
    st.session_state.reward_checked_animation = False


# --- 処理関数 ---

def record_success():
    """達成ボタンが押されたときの処理"""
    if st.session_state.current_day <= GOAL_MASU:

        day_achieved = st.session_state.current_day  # 達成したマス番号

        # 現在のマスを達成済みとして記録
        st.session_state.history[day_achieved] = "達成"

        # 連続達成日数を加算
        st.session_state.consecutive_success += 1

        # アニメーションフラグの設定とトーストメッセージ
        if day_achieved == GOAL_MASU:
            # Day 25: ゴール達成 (風船+雪の最大演出)
            st.session_state.animation_type = "goal_celebration"
            st.toast("👑 GOAL達成！おめでとうございます！25日間継続できました！", icon="🎊")
        elif day_achieved in REWARD_DAYS:
            # ご褒美マス達成 (風船のみ)
            st.session_state.animation_type = "balloons"
            st.toast(f"🎁 ご褒美マス達成！おめでとうございます！", icon="✨")
        elif st.session_state.consecutive_success % 3 == 0:
            # 連続達成メッセージ
            st.toast(f"🎉 3日連続達成！偉い！ {st.session_state.consecutive_success}日連続記録更新中！", icon="🥳")
        else:
            st.toast("達成を記録しました！次の日も頑張りましょう！", icon="💪")

        # 次のマスへ進む (ゴール後は進まない)
        if st.session_state.current_day < GOAL_MASU:
            st.session_state.current_day += 1


def record_failure():
    """未達成ボタンが押されたときの処理"""
    st.session_state.history[st.session_state.current_day] = "未達成"
    st.session_state.consecutive_success = 0  # 連続達成日数をリセット
    st.toast("未達成を記録しました。また明日から気持ちを切り替えて！", icon="😭")


def update_reward_check(day):
    """ご褒美チェックボックスの更新処理"""
    is_checked = st.session_state[f"reward_check_{day}"]
    # チェックボックスの状態をセッションに反映
    st.session_state.rewards[day]["checked"] = is_checked

    # NEW: チェックが入ったら（ご褒美をGETしたら）アニメーションフラグを立てる
    if is_checked:
        st.session_state.reward_checked_animation = True


# --- UIのメインレイアウト ---
st.set_page_config(page_title="3日坊主すごろく", page_icon="🌟", layout="wide")

st.title("三日坊主防止すごろく（25マス）🌟")

# テーマ設定エリア
st.session_state.theme = st.text_input(
    "チャレンジテーマ（25日間の目標）",
    value=st.session_state.theme,
    placeholder="例: 毎日10ページ本を読む！"
)

st.subheader("今日の達成")

# 達成ボタンと未達成ボタン
col_success, col_fail, col_status = st.columns([1.5, 1.5, 3])

if col_success.button("達成した！🎉", use_container_width=True, type="primary",
                      disabled=st.session_state.current_day > GOAL_MASU):
    record_success()
    # 処理後に再描画
    st.rerun()

if col_fail.button("今日はできなかった...😢", use_container_width=True,
                   disabled=st.session_state.current_day > GOAL_MASU):
    record_failure()
    # 処理後に再描画
    st.rerun()

# --- アニメーションの実行（成功時の一度だけ） ---
# 1. 達成ボタンによるアニメーション
if st.session_state.animation_type == "balloons":
    st.balloons()
    st.session_state.animation_type = None
elif st.session_state.animation_type == "goal_celebration":
    # ゴール達成時は、風船と雪を両方飛ばし、最大限の演出をする
    st.balloons()
    st.snow()
    st.session_state.animation_type = None

# 2. NEW: ご褒美チェックボックスによるアニメーション
if st.session_state.reward_checked_animation:
    st.balloons()
    st.session_state.reward_checked_animation = False  # 実行後にリセット

# 現在のステータス表示
if st.session_state.current_day > GOAL_MASU:
    # NEW: ゴール達成時のメッセージを修正
    col_status.markdown("## 🎉 おめでとう！GOAL達成！✨")
else:
    col_status.markdown(
        f"現在の位置: **{st.session_state.current_day}マス** (残り{GOAL_MASU - st.session_state.current_day}日)"
    )
    col_status.markdown(
        f"連続達成日数: **{st.session_state.consecutive_success}日**"
    )

st.divider()

# --- すごろくとご褒美入力のメインエリア ---
col_game, col_reward = st.columns([3, 2])

with col_game:
    st.subheader("すごろく盤")

    # すごろく盤の描画ロジック
    masses = [
        [1, 2, 3, 4, 5],
        [6, 7, 8, 9, 10],
        [11, 12, 13, 14, 15],
        [16, 17, 18, 19, 20],
        [21, 22, 23, 24, 25]
    ]

    for row in masses:
        cols = st.columns(len(row))
        for i, num in enumerate(row):
            # マスのアイコンを決定
            is_current = (num == st.session_state.current_day)
            is_achieved = (num in st.session_state.history and st.session_state.history[num] == "達成")
            is_reward = (num in REWARD_DAYS)
            is_goal = (num == GOAL_MASU)

            if is_current:
                # 現在位置
                mark = "⭐"
            elif is_goal and is_achieved:
                # ゴール達成済み
                mark = "👑"
            elif is_reward and is_achieved:
                # ご褒美マス達成済み
                mark = "🎁"
            elif is_achieved:
                # 過去の達成マス
                mark = "✅"
            elif is_reward:
                # ご褒美マス
                mark = "🌼"
            elif is_goal:
                # ゴールマス
                mark = "🌟"
            else:
                # 通常マス
                mark = "⚪"

            # HTML/CSSでマスのデザインを調整
            # 現在位置のマスは少し目立つように装飾
            style = ""
            if is_current:
                style = "border: 2px solid #FF4B4B; background-color: #FFF0F0; border-radius: 8px; padding: 5px;"
            elif is_achieved:
                style = "background-color: #D4EDDA; border-radius: 8px; padding: 5px;"
            elif is_reward:
                style = "background-color: #FFF3CD; border-radius: 8px; padding: 5px;"

            cols[i].markdown(
                f"""
                <div style='text-align:center; {style}'>
                    <span style='font-size:30px;'>{mark}</span><br>
                    <small style='font-size:14px; font-weight:bold;'>{num}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

with col_reward:
    st.subheader("ご褒美リスト")
    st.markdown("ご褒美マスに到達するたびに、自分へのご褒美を記録しましょう！")

    # ご褒美入力とチェックボックスの描画
    for day in REWARD_DAYS:
        # ご褒美の入力フィールド
        reward_name = st.session_state.rewards[day]["name"]

        # ご褒美マスに到達したか、または過去に達成しているか
        can_check = (day <= st.session_state.current_day)

        # ご褒美入力欄
        st.session_state.rewards[day]["name"] = st.text_input(
            f"**Day {day} のご褒美**",
            value=reward_name,
            key=f"reward_name_{day}",
            placeholder="例: 好きなケーキを買う、映画を見る",
            label_visibility="visible" if reward_name else "collapsed"  # 既に入力されていればラベルを表示
        )

        # ご褒美のチェックボックス（ご褒美マスに到達したら有効化）
        if st.session_state.rewards[day]["name"]:
            # チェックボックスの状態をセッションに保存
            st.checkbox(
                f"GET: {st.session_state.rewards[day]['name']}",
                value=st.session_state.rewards[day]["checked"],
                key=f"reward_check_{day}",
                on_change=update_reward_check,  # チェック時に状態を更新する関数を呼び出し
                args=(day,),
                disabled=not can_check
            )

# --- 達成履歴（サイドバーに移動） ---
with st.sidebar:
    st.subheader("達成履歴")
    if st.session_state.history:
        # 達成したマスのリストを表示
        achieved_days = [day for day, status in st.session_state.history.items() if status == "達成"]
        st.markdown(f"**累計達成日数: {len(achieved_days)}日**")
        st.write("---")

        # 履歴を逆順に表示して最新の記録を見やすくする
        for day in sorted(st.session_state.history.keys(), reverse=True):
            status = st.session_state.history[day]
            icon = "✅" if status == "達成" else "❌"
            st.markdown(f"{icon} **Day {day}:** {status}")
    else:
        st.info("まだ記録がありません。チャレンジを開始しましょう！")

st.markdown("---")
st.caption(f"現在のチャレンジテーマ: **{st.session_state.theme}**")

# --- デバッグ/リセット機能 (必要であればコメントアウトを外す) ---
if st.button("リセット"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()