import streamlit as st
import json
import os

# --- 定数と設定 ---
MAX_MASU = 25
REWARD_DAYS = [3, 7, 14, 21, 25]
START_MASU = 1
GOAL_MASU = MAX_MASU
DATA_FILE = "sugoroku_data.json"  # データを保存するファイル名


# --- データの永続化関数 ---
# ... (load_data, save_data 関数は変更なし) ...

def load_data():
    """保存されたデータをファイルから読み込む"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                # 辞書型としてデータを読み込む
                return json.load(f)
            except json.JSONDecodeError:
                # ファイルが空や破損している場合
                st.error("保存ファイルが破損しています。新しいチャレンジを開始します。")
                return {}
    return {}  # ファイルが存在しない場合は空の辞書を返す


def save_data():
    """現在のアプリの状態をファイルに保存する"""
    data_to_save = {
        "current_day": st.session_state.current_day,
        "history": st.session_state.history,
        "rewards": st.session_state.rewards,
        "consecutive_success": st.session_state.consecutive_success,
        "theme": st.session_state.theme,  # テーマも保存
    }
    # JSON形式でファイルに書き込む
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)


# --- 処理関数 ---

def reset_game():
    """ゲームの状態を初期値にリセットする (テーマは除く)"""
    st.session_state.current_day = 1
    st.session_state.history = {}
    st.session_state.rewards = {day: {"name": "", "checked": False} for day in REWARD_DAYS}
    st.session_state.consecutive_success = 0
    st.session_state.animation_type = None
    st.session_state.reward_checked_animation = False

    st.toast("チャレンジをリセットしました！", icon="🗑️")
    save_data()  # リセット後、データを保存
    # st.rerun() は削除済み


def record_success():
    """達成ボタンが押されたときの処理"""
    if st.session_state.current_day <= GOAL_MASU:

        day_achieved = st.session_state.current_day  # 達成したマス番号

        # 現在のマスを達成済みとして記録 (キーはint)
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
        elif st.session_state.consecutive_success > 0 and st.session_state.consecutive_success % 3 == 0:  # 連続達成日数が0でないことを確認
            # 連続達成メッセージ
            st.toast(f"🎉 3日連続達成！偉い！ {st.session_state.consecutive_success}日連続記録更新中！", icon="🥳")
        else:
            st.toast("達成を記録しました！次の日も頑張りましょう！", icon="💪")

        # 次のマスへ進む (Day 25達成時はDay 26に進み、ボタンを無効化する)
        if st.session_state.current_day <= GOAL_MASU:
            st.session_state.current_day += 1

    save_data()  # 達成記録後、データを保存
    # Session State (current_day, history, consecutive_success)が更新されるため、st.rerun()は不要


def record_failure():
    """未達成ボタンが押されたときの処理"""
    if st.session_state.current_day <= GOAL_MASU:  # ゴール後は未達成も記録しない
        # キーはint
        st.session_state.history[st.session_state.current_day] = "未達成"
        st.session_state.consecutive_success = 0  # 連続達成日数をリセット
        st.toast("未達成を記録しました。また明日から気持ちを切り替えて！", icon="😭")

        save_data()  # 失敗記録後、データを保存
        # st.rerun() # Session Stateが更新されるため、st.rerun()は削除


def update_reward_check(day):
    """ご褒美チェックボックスの更新処理"""
    is_checked = st.session_state[f"reward_check_{day}"]
    # チェックボックスの状態をセッションに反映
    st.session_state.rewards[day]["checked"] = is_checked

    # チェックが入ったら（ご褒美をGETしたら）アニメーションフラグを立てる
    if is_checked:
        st.session_state.reward_checked_animation = True

    save_data()  # チェック状態変更後、データを保存


# --- 初期化（アプリ起動時に一度だけ動く） ---

# 1. 永続化されたデータのロード
loaded_data = load_data()

# 2. セッションステートへの反映と初期値設定
# 'current_day'がセッションに存在しない場合のみ、ロードまたは初期値で設定する
if "current_day" not in st.session_state:

    # 基本データのロード
    st.session_state.current_day = loaded_data.get("current_day", 1)
    st.session_state.consecutive_success = loaded_data.get("consecutive_success", 0)
    st.session_state.theme = loaded_data.get("theme", "読書を25日継続する！")

    # --- history データのロードとキーの整数化 ---
    loaded_history = loaded_data.get("history", {})
    # JSONから読み込まれたキー（文字列）を、Pythonで扱いやすい整数に変換し直す
    st.session_state.history = {}
    for key, value in loaded_history.items():
        try:
            st.session_state.history[int(key)] = value
        except ValueError:
            # 整数に変換できないキー（予期せぬデータ）はスキップ
            continue

    # ご褒美データのロード（初期構造を保証）
    initial_rewards = {day: {"name": "", "checked": False} for day in REWARD_DAYS}
    loaded_rewards = loaded_data.get("rewards", {})

    # ロードデータと初期構造をマージ（新しいご褒美マスが増えた場合などに備える）
    st.session_state.rewards = initial_rewards
    for day in REWARD_DAYS:
        # JSONのキーは文字列なので、文字列キーでアクセスを試みる
        key = str(day)
        if key in loaded_rewards:
            st.session_state.rewards[day] = loaded_rewards[key]
        elif day in loaded_rewards:  # 念のため整数キーもチェック
            st.session_state.rewards[day] = loaded_rewards[day]

    # アニメーションフラグの初期化（アプリ起動時はアニメーション不要）
    st.session_state.animation_type = None
    st.session_state.reward_checked_animation = False

# --- UIのメインレイアウト ---
st.set_page_config(page_title="3日坊主すごろく", page_icon="🌟", layout="wide")

st.title("三日坊主防止すごろく（25マス）🌟")

# テーマ設定とリセットボタンのエリア
col_theme, col_reset = st.columns([4, 1])

with col_theme:
    st.session_state.theme = st.text_input(
        "チャレンジテーマ（25日間の目標）",
        value=st.session_state.theme,
        key="theme_input",  # keyを設定して永続化されたテーマと紐付け
        placeholder="例: 毎日10ページ本を読む！"
    )

with col_reset:
    # リセットボタン (on_clickでreset_gameを呼び出す)
    st.button("🔄 チャレンジをリセット", on_click=reset_game, use_container_width=True)

st.subheader("今日の達成")

# 達成ボタンと未達成ボタン
col_success, col_fail, col_status = st.columns([1.5, 1.5, 3])

# ゴール達成後はボタンを無効化 (current_day > GOAL_MASU で無効)
is_goal_achieved = st.session_state.current_day > GOAL_MASU

if col_success.button("達成した！🎉", use_container_width=True, type="primary", disabled=is_goal_achieved):
    record_success()
    # 処理後に再描画: Session Stateが変更されるため、st.rerun()は削除
    # st.rerun()

if col_fail.button("今日はできなかった...😢", use_container_width=True, disabled=is_goal_achieved):
    # record_failure()内で Session Stateが変更されるため、st.rerun()は削除
    record_failure()

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

# 2. ご褒美チェックボックスによるアニメーション
if st.session_state.reward_checked_animation:
    st.balloons()
    st.session_state.reward_checked_animation = False  # 実行後にリセット

# 現在のステータス表示
if is_goal_achieved:
    # ゴール達成時のメッセージを修正
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

            # historyのキーは初期化時に整数に統一されたため、ここではnum (int)で直接チェック
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
        # 修正: 'is_checked' も含めて判定することで、一度チェックしたものはリセット後も操作可能にする
        is_checked = st.session_state.rewards[day]["checked"]
        can_check = (day <= st.session_state.current_day) or is_checked

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
                value=is_checked,  # 既に定義された is_checked を使用
                key=f"reward_check_{day}",
                on_change=update_reward_check,  # チェック時に状態を更新する関数を呼び出し
                args=(day,),
                disabled=not can_check
            )

# --- 達成履歴（サイドバーに移動） ---
with st.sidebar:
    st.subheader("達成履歴")
    if st.session_state.history:
        # historyのキーは初期化時に整数に統一されたため、int(day)で直接アクセス
        sorted_days = sorted(st.session_state.history.keys(), reverse=True)

        # 達成したマスのリストを表示
        achieved_days = [day for day in sorted_days if st.session_state.history[day] == "達成"]
        st.markdown(f"**累計達成日数: {len(achieved_days)}日**")
        st.write("---")

        # 履歴を逆順に表示して最新の記録を見やすくする
        for day in sorted_days:
            # historyのキーは整数なので、dayで直接アクセス
            status = st.session_state.history[day]
            icon = "✅" if status == "達成" else "❌"
            st.markdown(f"{icon} **Day {day}:** {status}")
    else:
        st.info("まだ記録がありません。チャレンジを開始しましょう！")

st.markdown("---")
st.caption(f"現在のチャレンジテーマ: **{st.session_state.theme}**")
st.caption("※このデータは、アプリが動作しているPCのローカルファイルに保存されます。")