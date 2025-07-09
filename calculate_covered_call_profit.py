import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

# --- Helper Functions (无需改动) ---
def get_float_input(prompt):
    while True:
        try: return float(input(prompt))
        except ValueError: print("输入无效，请输入一个有效的数字。")

def get_int_input(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value > 0: return value
            else: print("请输入一个正整数。")
        except ValueError: print("输入无效，请输入一个有效的整数。")

# --- Calculation Functions (无需改动) ---
def calculate_covered_call_profit(expiration_price, purchase_price, strike_price, premium_per_share, num_shares):
    total_premium = premium_per_share * num_shares
    if expiration_price <= strike_price:
        stock_profit = (expiration_price - purchase_price) * num_shares
    else:
        stock_profit = (strike_price - purchase_price) * num_shares
    return stock_profit + total_premium

def calculate_buy_and_hold_profit(expiration_price, purchase_price, num_shares):
    return (expiration_price - purchase_price) * num_shares


# --- 主程序 ---
def main():
    print("--- 备兑看涨期权 (Covered Call) 动态收益分析工具 ---")
    
    # 1. 获取基本参数
    purchase_price = get_float_input("请输入您的正股买入均价: ")
    num_contracts = get_int_input("请输入您卖出的看涨期权合约数量 (1合约=100股): ")
    num_shares = num_contracts * 100
    strike_price = get_float_input(f"请输入期权的行权价 (Strike Price): ")
    premium_per_share = get_float_input("请输入您收到的每股权利金 (Premium): ")
    initial_expiration_price = get_float_input("请输入滑块的初始到期日股价: ")
    print("-" * 30)
    print("正在生成交互式图表...")

    try:
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
    except:
        print("\n注意：未找到中文字体'SimHei'，图表中的中文可能无法显示。")

    # 2. 创建图表和坐标轴
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.subplots_adjust(bottom=0.25)

    # 3. 绘制静态背景曲线
    plot_min_price = min(purchase_price, strike_price) * 0.8
    plot_max_price = (strike_price + premium_per_share) * 1.2 # 确保交叉点在视图内
    expiration_prices = np.linspace(plot_min_price, plot_max_price, 400)

    cc_profits = [calculate_covered_call_profit(p, purchase_price, strike_price, premium_per_share, num_shares) for p in expiration_prices]
    bh_profits = [calculate_buy_and_hold_profit(p, purchase_price, num_shares) for p in expiration_prices]

    ax.plot(expiration_prices, cc_profits, label='备兑看涨期权 (Covered Call)', color='blue', linewidth=2, zorder=2)
    ax.plot(expiration_prices, bh_profits, label='仅持有正股 (Buy & Hold)', color='orange', linestyle='--', linewidth=2, zorder=2)
    
    ax.axhline(0, color='black', linestyle='-', linewidth=0.7)
    ax.axvline(purchase_price, color='red', linestyle=':', label=f'买入价: ${purchase_price:.2f}')
    
    # --- 新增功能 1：计算并标记关键点 ---
    # 最大收益点 (发生在行权价)
    max_profit = calculate_covered_call_profit(strike_price, purchase_price, strike_price, premium_per_share, num_shares)
    ax.plot(strike_price, max_profit, 'go', markersize=10, zorder=4, label=f'最大收益点 (at Strike)')
    ax.annotate(f'最大收益: ${max_profit:,.2f}',
                xy=(strike_price, max_profit),
                xytext=(strike_price - (plot_max_price-plot_min_price)*0.1, max_profit * 0.9),
                arrowprops=dict(facecolor='green', shrink=0.05, width=1, headwidth=5),
                fontsize=9, bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="black", lw=1, alpha=0.7))

    # 策略交叉点
    crossover_price = strike_price + premium_per_share
    crossover_profit = calculate_buy_and_hold_profit(crossover_price, purchase_price, num_shares)
    ax.plot(crossover_price, crossover_profit, 'mo', markersize=10, zorder=4, label='策略交叉点')
    ax.axvline(crossover_price, color='magenta', linestyle=':', label=f'交叉价格: ${crossover_price:.2f}')
    ax.annotate(f'股价 > ${crossover_price:.2f}\n持股收益更高',
                xy=(crossover_price, crossover_profit),
                xytext=(crossover_price, crossover_profit * 0.5),
                arrowprops=dict(facecolor='magenta', shrink=0.05, width=1, headwidth=5),
                fontsize=9, ha='center', bbox=dict(boxstyle="round,pad=0.3", fc="magenta", ec="black", lw=1, alpha=0.3))


    # 4. 绘制初始动态元素
    cc_marker, = ax.plot([], [], 'b*', markersize=15, zorder=5)
    bh_marker, = ax.plot([], [], 'o', color='orange', markersize=10, zorder=5)
    summary_text_obj = fig.text(0.02, 0.98, "", ha="left", va="top", fontsize=10, bbox=dict(boxstyle='round,pad=0.5', fc='aliceblue', alpha=0.8))

    # 5. 定义更新函数
    def update(val):
        current_price = val
        cc_profit = calculate_covered_call_profit(current_price, purchase_price, strike_price, premium_per_share, num_shares)
        bh_profit = calculate_buy_and_hold_profit(current_price, purchase_price, num_shares)

        cc_marker.set_data([current_price], [cc_profit])
        bh_marker.set_data([current_price], [bh_profit])

        difference = cc_profit - bh_profit
        if abs(difference) < 0.01:
             conclusion_str = "结论：两种策略收益几乎相等。"
        elif difference > 0:
            conclusion_str = f"结论：Covered Call 策略比仅持股多赚了 ${difference:,.2f}"
        else:
            conclusion_str = f"结论：Covered Call 策略比仅持股少赚了 ${abs(difference):,.2f}"
        
        new_summary_text = (
            f"--- 在到期日股价为 ${current_price:.2f} 时的收益分析 ---\n\n"
            f"策略一 (Covered Call) 总收益: ${cc_profit:,.2f}\n"
            f"策略二 (仅持有正股) 总收益: ${bh_profit:,.2f}\n\n"
            f"{conclusion_str}"
        )
        summary_text_obj.set_text(new_summary_text)
        fig.canvas.draw_idle()

    # 6. 创建滑块
    ax_slider = fig.add_axes([0.2, 0.05, 0.65, 0.03])
    price_slider = Slider(
        ax=ax_slider,
        label='拖动我!\n到期日股价',
        valmin=plot_min_price,
        valmax=plot_max_price,
        valinit=initial_expiration_price,
        valstep=(plot_max_price - plot_min_price) / 400
    )
    
    price_slider.on_changed(update)
    update(initial_expiration_price)
    
    # 7. 设置最终图表样式
    ax.set_title('备兑看涨期权 vs 仅持有正股 动态收益分析', fontsize=16, pad=20)
    ax.set_xlabel('到期日股票市价 ($)', fontsize=12)
    ax.set_ylabel(f'基于 {num_shares} 股的总收益/亏损 ($)', fontsize=12)
    ax.legend(loc='lower right')
    ax.grid(True)
    
    plt.show()

if __name__ == "__main__":
    main()