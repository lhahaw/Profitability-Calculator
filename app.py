from flask import Flask, request, render_template
import os
app = Flask(__name__)

# 默认参数（和你Excel模型一致，可根据你的实际情况微调）

DEFAULTS = {
    # ==== 核心假设 Core Assumptions ====
    # 合理开局时租（含毛利空间，可按市场和品牌再调）
    "hourly_sell_price": 4600.0,       # NZD/hr 建议初始定价
    # 主场景利用率，用于 KPI 计算（情景分析有单独场景）
    "annual_hours": 600.0,

    # ==== 每小时变动成本 Variable Costs per Flight Hour (NZD/hr) ====

    # 燃油：Phenom 100 大约 430 L/hr，Jet A1 约 1.25 NZD/L（含服务费估算）
    "fuel_burn": 430.0,                # L/hr
    "fuel_price": 1.25,                # NZD/L
    # 自动算燃油成本 = 约 430 * 1.25 = 538 NZD/hr，实际计算由程序完成

    # 维护与预提（结合澳新市场，相比美国数据适度下调，更贴近自有/小型机队）
    "maint_airframe": 200.0,           # Airframe reserve
    "maint_engine": 700.0,             # Engine program / reserve
    "maint_other": 150.0,              # Other maint reserves

    # 导航、起降、地面服务等（按区域机场适中水平预估）
    "nav_atc": 80.0,                   # Nav & ATC fees
    "landing_parking": 70.0,           # Landing & parking
    "handling_catering": 80.0,         # Handling & simple catering
    "var_other": 60.0,                 # Other variable costs

    # 上述加总示意：
    # 燃油 ~538 + 维护(200+700+150=1050) + 其他(80+70+80+60=290)
    # 合计约 1,878 NZD/hr 作为默认变动成本水平

    # ==== 年度固定成本 Annual Fixed Costs (NZD/year) ====

    # 机组：以澳新中高端业务航空水平配置双机组 + 补贴
    "crew_captain": 190000.0,          # Captain salary
    "crew_fo": 120000.0,               # First Officer salary
    "crew_allowance": 25000.0,         # Allowances / per diem

    # 训练、保险、机库等
    "training": 25000.0,               # Sim, checks, OPC/LPC etc.
    "insurance": 45000.0,              # Hull + liability
    "hangar": 35000.0,                 # Hangar/parking (regional field)

    # 管理与支持成本
    "management": 45000.0,             # Back-office/admin/ops mgmt
    "compliance": 15000.0,             # Part 135 compliance, QA, SMS
    "marketing": 15000.0,              # Website, sales, client mgmt
    "finance": 80000.0,                # Lease/loan cost rough allowance
    "fixed_other": 20000.0,            # Misc fixed overhead

    # 合计约：
    # 190k + 120k + 25k + 25k + 45k + 35k + 45k + 15k + 15k + 80k + 20k
    # = 615,000 NZD/year 固定成本（适中偏稳健）

    # ==== 目标利润率 Target Margin ====
    "target_margin": 0.20,             # 20% 毛利目标（可调整）

    # ==== 情景小时数 Scenario Hours ====
    # 用于对比不同利用率时的单位成本 & 年度利润
    "scenario_1": 400,
    "scenario_2": 600,
    "scenario_3": 800,
    "scenario_4": 1000,
}


def get_value(form, key):
    """从表单取值，若为空或非法则使用默认值。"""
    raw = form.get(key, "").strip()
    if raw == "":
        return DEFAULTS[key]
    try:
        return float(raw)
    except ValueError:
        return DEFAULTS[key]


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 读取输入
        hourly_sell_price = get_value(request.form, "hourly_sell_price")
        annual_hours = get_value(request.form, "annual_hours")

        fuel_burn = get_value(request.form, "fuel_burn")
        fuel_price = get_value(request.form, "fuel_price")
        maint_airframe = get_value(request.form, "maint_airframe")
        maint_engine = get_value(request.form, "maint_engine")
        maint_other = get_value(request.form, "maint_other")
        nav_atc = get_value(request.form, "nav_atc")
        landing_parking = get_value(request.form, "landing_parking")
        handling_catering = get_value(request.form, "handling_catering")
        var_other = get_value(request.form, "var_other")

        crew_captain = get_value(request.form, "crew_captain")
        crew_fo = get_value(request.form, "crew_fo")
        crew_allowance = get_value(request.form, "crew_allowance")
        training = get_value(request.form, "training")
        insurance = get_value(request.form, "insurance")
        hangar = get_value(request.form, "hangar")
        management = get_value(request.form, "management")
        compliance = get_value(request.form, "compliance")
        marketing = get_value(request.form, "marketing")
        finance = get_value(request.form, "finance")
        fixed_other = get_value(request.form, "fixed_other")

        target_margin = get_value(request.form, "target_margin")

        scenario_hours = [
            get_value(request.form, "scenario_1"),
            get_value(request.form, "scenario_2"),
            get_value(request.form, "scenario_3"),
            get_value(request.form, "scenario_4"),
        ]
    else:
        # 初次加载用默认值
        hourly_sell_price = DEFAULTS["hourly_sell_price"]
        annual_hours = DEFAULTS["annual_hours"]

        fuel_burn = DEFAULTS["fuel_burn"]
        fuel_price = DEFAULTS["fuel_price"]
        maint_airframe = DEFAULTS["maint_airframe"]
        maint_engine = DEFAULTS["maint_engine"]
        maint_other = DEFAULTS["maint_other"]
        nav_atc = DEFAULTS["nav_atc"]
        landing_parking = DEFAULTS["landing_parking"]
        handling_catering = DEFAULTS["handling_catering"]
        var_other = DEFAULTS["var_other"]

        crew_captain = DEFAULTS["crew_captain"]
        crew_fo = DEFAULTS["crew_fo"]
        crew_allowance = DEFAULTS["crew_allowance"]
        training = DEFAULTS["training"]
        insurance = DEFAULTS["insurance"]
        hangar = DEFAULTS["hangar"]
        management = DEFAULTS["management"]
        compliance = DEFAULTS["compliance"]
        marketing = DEFAULTS["marketing"]
        finance = DEFAULTS["finance"]
        fixed_other = DEFAULTS["fixed_other"]

        target_margin = DEFAULTS["target_margin"]

        scenario_hours = [
            DEFAULTS["scenario_1"],
            DEFAULTS["scenario_2"],
            DEFAULTS["scenario_3"],
            DEFAULTS["scenario_4"],
        ]

    # ===== 计算部分（沿用Excel逻辑） =====

    # 变动成本 / hr
    fuel_cost = fuel_burn * fuel_price
    total_var_per_hr = (
        fuel_cost
        + maint_airframe
        + maint_engine
        + maint_other
        + nav_atc
        + landing_parking
        + handling_catering
        + var_other
    )

    # 固定成本 / 年
    total_fixed_per_year = (
        crew_captain
        + crew_fo
        + crew_allowance
        + training
        + insurance
        + hangar
        + management
        + compliance
        + marketing
        + finance
        + fixed_other
    )

    # 基础模型（主场景）
    fixed_per_hr = total_fixed_per_year / annual_hours if annual_hours > 0 else 0
    total_cost_per_hr = total_var_per_hr + fixed_per_hr
    profit_per_hr = hourly_sell_price - total_cost_per_hr
    margin_per_hr = (profit_per_hr / hourly_sell_price) if hourly_sell_price > 0 else 0

    annual_revenue = hourly_sell_price * annual_hours
    annual_var_cost = total_var_per_hr * annual_hours
    annual_profit = annual_revenue - annual_var_cost - total_fixed_per_year

    breakeven_rate = total_cost_per_hr
    target_rate = (
        total_cost_per_hr / (1 - target_margin)
        if (1 - target_margin) > 0
        else None
    )

    # 情景分析
    scenarios = []
    for h in scenario_hours:
        if h and h > 0:
            scen_fixed_per_hr = total_fixed_per_year / h
            scen_total_per_hr = total_var_per_hr + scen_fixed_per_hr
            scen_breakeven = scen_total_per_hr
            scen_sell = hourly_sell_price
            scen_profit = (scen_sell - scen_total_per_hr) * h
            scenarios.append(
                {
                    "hours": h,
                    "var_per_hr": total_var_per_hr,
                    "fixed_per_hr": scen_fixed_per_hr,
                    "total_per_hr": scen_total_per_hr,
                    "breakeven": scen_breakeven,
                    "sell_rate": scen_sell,
                    "annual_profit": scen_profit,
                }
            )
        else:
            scenarios.append(
                {
                    "hours": h,
                    "var_per_hr": 0,
                    "fixed_per_hr": 0,
                    "total_per_hr": 0,
                    "breakeven": 0,
                    "sell_rate": hourly_sell_price,
                    "annual_profit": 0,
                }
            )

    context = dict(
        # inputs
        hourly_sell_price=hourly_sell_price,
        annual_hours=annual_hours,
        fuel_burn=fuel_burn,
        fuel_price=fuel_price,
        maint_airframe=maint_airframe,
        maint_engine=maint_engine,
        maint_other=maint_other,
        nav_atc=nav_atc,
        landing_parking=landing_parking,
        handling_catering=handling_catering,
        var_other=var_other,
        crew_captain=crew_captain,
        crew_fo=crew_fo,
        crew_allowance=crew_allowance,
        training=training,
        insurance=insurance,
        hangar=hangar,
        management=management,
        compliance=compliance,
        marketing=marketing,
        finance=finance,
        fixed_other=fixed_other,
        target_margin=target_margin,
        scenario_1=scenario_hours[0],
        scenario_2=scenario_hours[1],
        scenario_3=scenario_hours[2],
        scenario_4=scenario_hours[3],

        # computed
        fuel_cost=fuel_cost,
        total_var_per_hr=total_var_per_hr,
        total_fixed_per_year=total_fixed_per_year,
        fixed_per_hr=fixed_per_hr,
        total_cost_per_hr=total_cost_per_hr,
        profit_per_hr=profit_per_hr,
        margin_per_hr=margin_per_hr,
        annual_revenue=annual_revenue,
        annual_var_cost=annual_var_cost,
        annual_profit=annual_profit,
        breakeven_rate=breakeven_rate,
        target_rate=target_rate,
        scenarios=scenarios,
    )

    return render_template("index.html", **context)


if __name__ == "__main__":
    # 本地开发用：在 5000 端口跑
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)