import matplotlib.pyplot as plt
import numpy as np

# --- Helper Functions ---
def get_float_input(prompt):
    """循环提示用户，直到输入一个有效的浮点数。"""
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("输入无效，请输入一个有效的数字。")

def get_int_input(prompt):
    """循环提示用户，直到输入一个有效的整数。"""
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
            else:
                print("请输入一个正整数。")
        except ValueError:
            print("输入无效，请输入一个有效的整数。")

# --- Calculation Functions ---
def calculate_covered_call_profit(expiration_price, purchase_price, strike_price, premium_per_share, num_shares):
    """计算备兑看涨期权策略的收益。"""
    total_premium = premium_per_share * num_shares
    if expiration_price <= strike_price:
        stock_profit = (expiration_price - purchase_price) * num_shares
    else:
        stock_profit = (strike_price - purchase_price) * num_shares
    return stock_profit + total_premium

def calculate_buy_and_hold_profit(expiration_price, purchase_price, num_shares):
    """计算仅持有正股策略的收益。"""
    return (expiration_price - purchase_price) * num_shares


# --- Main Program ---
def main():
    print("--- 备兑看涨期权 (Covered Call) 收益分析工具 ---")
    
    # 1. 交互式获取用户输入
    purchase_price = get_float_input("请输入您的正股买入均价: ")
    num_contracts = get_int_input("请输入您卖出的看涨期权合约数量 (1合约=100股): ")
    num_shares = num_contracts * 100
    strike_price = get_float_input(f"请输入期权的行权价 (Strike Price): ")
    premium_per_share = get_float_input("请输入您收到的每股权利金 (Premium): ")
    specific_expiration_price = get_float_input("请输入您想计算的特定到期日股价: ")
    print("-" * 30)

    # 2. 计算指定到期日股价的收益
    cc_profit_specific = calculate_covered_call_profit(specific_expiration_price, purchase_price, strike_price, premium_per_share, num_shares)
    bh_profit_specific = calculate_buy_and_hold_profit(specific_expiration_price, purchase_price, num_shares)

    # 打印到控制台
    print(f"\n--- 在到期日股价为 ${specific_expiration_price:.2f} 时的收益分析 ---")
    print(f"策略一：备兑看涨期权 (Covered Call) 的总收益为: ${cc_profit_specific:,.2f}")
    print(f"策略二：仅持有正股 (Buy & Hold) 的总收益为: ${bh_profit_specific:,.2f}")
    
    difference = cc_profit_specific - bh_profit_specific
    if difference >= 0:
        conclusion_str = f"结论：Covered Call 策略比仅持股多赚了 ${difference:,.2f}"
    else:
        conclusion_str = f"结论：Covered Call 策略比仅持股少赚了 ${abs(difference):,.2f}"
    print(conclusion_str)
    print("-" * 30)

    # 3. 准备在图上显示的文本
    summary_text = (
        f"--- 在到期日股价为 ${specific_expiration_price:.2f} 时的收益分析 ---\n\n"
        f"策略一 (Covered Call) 总收益: ${cc_profit_specific:,.2f}\n"
        f"策略二 (仅持有正股) 总收益: ${bh_profit_specific:,.2f}\n\n"
        f"{conclusion_str}"
    )

    # 4. 绘制收益曲线图
    try:
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
    except:
        print("\n注意：未找到中文字体'SimHei'，图表中的中文可能无法显示。")

    plot_min_price = min(purchase_price, strike_price) - 30
    plot_max_price = max(purchase_price, strike_price) + 30
    expiration_prices = np.linspace(plot_min_price, plot_max_price, 400)

    covered_call_profits = [calculate_covered_call_profit(p, purchase_price, strike_price, premium_per_share, num_shares) for p in expiration_prices]
    buy_and_hold_profits = [calculate_buy_and_hold_profit(p, purchase_price, num_shares) for p in expiration_prices]

    fig, ax = plt.subplots(figsize=(13, 8))
    ax.plot(expiration_prices, covered_call_profits, label='备兑看涨期权 (Covered Call)', color='blue', linewidth=2)
    ax.plot(expiration_prices, buy_and_hold_profits, label='仅持有正股 (Buy & Hold)', color='orange', linestyle='--', linewidth=2)

    ax.plot(specific_expiration_price, cc_profit_specific, 'b*', markersize=12, zorder=5, label=f'查询点 (Covered Call)')
    ax.plot(specific_expiration_price, bh_profit_specific, 'o', color='orange', markersize=8, zorder=5, label=f'查询点 (Buy & Hold)')

    ax.axhline(0, color='black', linestyle='-', linewidth=0.7)
    ax.axvline(purchase_price, color='red', linestyle=':', label=f'买入价: ${purchase_price:.2f}')
    ax.axvline(strike_price, color='green', linestyle=':', label=f'行权价: ${strike_price:.2f}')

    # --- 新增功能：将文本框添加到图表上 ---
    # 使用 fig.text 在图形坐标系中放置文本，(0.13, 0.86) 代表从左到右13%，从下到上86%的位置
    fig.text(0.13, 0.86, summary_text, 
             ha="left", va="top",
             fontsize=10, 
             bbox=dict(boxstyle='round,pad=0.5', fc='aliceblue', alpha=0.8))


    ax.set_title('备兑看涨期权 vs 仅持有正股 收益曲线对比', fontsize=16, pad=20)
    ax.set_xlabel('到期日股票市价 ($)', fontsize=12)
    ax.set_ylabel(f'基于 {num_shares} 股的总收益/亏损 ($)', fontsize=12)
    ax.legend(loc='lower right')
    ax.grid(True)
    
    fig.tight_layout(rect=[0, 0, 1, 0.95]) # 调整布局为标题留出空间

    file_name = 'final_covered_call_analysis.png'
    plt.savefig(file_name)
    print(f"\n分析图表已生成，并保存为 '{file_name}'")
    plt.show()

if __name__ == "__main__":
    main()