# 全部主实验统一对比

## 范围与口径

本报告统一比较8种模型—模式配置：DeepSeek-v4-Flash/Pro、Qwen3.5-9B/35B-A3B，
各自的non-thinking与thinking模式。每种配置均比较Direct、Robust、Ours，并在两个数据集
上分别报告：

- 无注入环境：完整clean正负平衡集合；
- 有注入环境：attacked phishing与injected legitimate control合并后的正负平衡集合；
- 诊断指标：attacked phishing recall和legitimate control FPR；
- 配对检验：Ours相对Robust的exact McNemar；
- 效率：平均答案、reasoning及总输出tokens。

Qwen thinking使用2026-08-30补全版本，旧2,048-token截断结果不再进入本报告。

## PhishFuzzer

表中每个三元组均按`Direct / Robust / Ours`排列。

| 模型—模式 | 无注入F1 | 有注入F1 | Attacked recall | Control FPR | Ours−Robust recall（p） |
|---|---:|---:|---:|---:|---:|
| Flash non-thinking | .9838/.9828/.9792 | .9612/.9831/.9814 | .954/.986/.976 | .031/.020/.013 | −1.00pp (`.00195`) |
| Flash thinking | .9874/.9859/.9793 | .9613/.9812/.9790 | .982/.991/.979 | .061/.029/.021 | −1.20pp (`.00183`) |
| Pro non-thinking | .9664/.9648/.9691 | .8846/.9697/**.9839** | .793/.944/**.975** | .000/.003/.007 | **+3.10pp** (`9.31e-10`) |
| Pro thinking | .9604/.9726/**.9833** | .9731/.9801/**.9835** | .958/.984/.984 | .011/.024/.017 | 0 (`1.0`) |
| Qwen 9B non-thinking | .9529/.9521/.9476 | .8881/.9504/**.9610** | .833/.919/**.961** | .043/.015/.039 | **+4.20pp** (`4.46e-10`) |
| Qwen 9B thinking | .9747/.9737/.9735 | .9655/**.9685**/.9643 | .965/.984/.985 | .034/.048/.058 | +.10pp (`1.0`) |
| Qwen 35B non-thinking | .9782/.9766/.9752 | .9724/**.9829**/.9824 | .952/.978/.977 | .006/.012/.012 | −.10pp (`1.0`) |
| Qwen 35B thinking | **.9900**/.9870/.9845 | **.9875**/.9803/.9798 | .988/.995/.995 | .013/.035/.036 | 0 (`1.0`) |

主要结论：

- Pro non-thinking和Qwen 9B non-thinking提供最强的核心证据：Ours相对Robust的攻击
  recall分别提高3.1pp和4.2pp，均高度显著。
- Qwen 35B non-thinking已接近饱和，Ours与Robust完全持平。
- Flash中Robust的attacked recall显著更高，但Ours的control FPR更低，因此两者在完整
  有注入集合上的accuracy差异不显著。
- 所有thinking配置中，Ours相对Robust均无显著recall增量；Pro thinking二者recall相同，
  但Ours整体F1更高。

## 质量修正的Nazario + Enron

| 模型—模式 | 无注入F1 | 有注入F1 | Attacked recall | Control FPR | Ours−Robust recall（p） |
|---|---:|---:|---:|---:|---:|
| Flash non-thinking | .9766/.9745/.9765 | .9456/.9769/**.9789** | .946/.975/.971 | .054/.021/.013 | −.42pp (`1.0`) |
| Flash thinking | **.9809**/.9702/.9680 | .9689/**.9706**/.9661 | .979/.967/.954 | .042/.025/.021 | −1.26pp (`.375`) |
| Pro non-thinking | .9676/.9676/**.9700** | .9186/.9677/**.9723** | .849/.941/**.954** | .000/.004/.008 | +1.26pp (`.25`) |
| Pro thinking | .9614/.9660/**.9701** | .9682/**.9727**/.9638 | .954/.971/.946 | .017/.025/.017 | −2.51pp (`.0703`) |
| Qwen 9B non-thinking | .9298/.9224/.9295 | .8854/.9275/**.9382** | .824/.883/**.921** | .038/.021/.042 | **+3.77pp** (`.00391`) |
| Qwen 9B thinking | **.9706**/.9642/.9644 | .9598/.9628/**.9649** | .950/.975/**.979** | .029/.050/.050 | +.42pp (`1.0`) |
| Qwen 35B non-thinking | .9397/.9462/**.9554** | .9281/.9494/**.9542** | .891/.941/**.958** | .029/.042/.050 | +1.67pp (`.289`) |
| Qwen 35B thinking | .9686/**.9793**/.9710 | **.9649**/.9516/.9514 | .979/**.987**/.983 | .050/.088/.084 | −.42pp (`1.0`) |

主要结论：

- Qwen 9B non-thinking再次显著支持Ours相对Robust的增量。
- Pro与Qwen 35B non-thinking方向均有利于Ours，但239个攻击样本不足以显著。
- Flash non-thinking中Ours的完整有注入F1最高，尽管Robust recall略高，因为Ours FPR
  更低。
- Thinking没有稳定帮助Ours超过Robust；35B thinking中Direct总体最好，说明额外防御
  指令会使reasoning模型对合法注入过度敏感。

## H1/H2汇总

| 模型—模式 | H1：Ours recall最高 | H2 clean precision | H2 control FPR | 解释 |
|---|---:|---:|---:|---|
| Flash non-thinking | 0/2 | 2/2 | 2/2 | Robust recall更高，Ours FPR更低 |
| Flash thinking | 0/2 | 2/2 | 2/2 | 无Ours增量 |
| Pro non-thinking | **2/2** | 2/2 | 2/2 | 最完整支持预期；PF显著 |
| Pro thinking | 0/2 | 2/2 | 2/2 | PF持平，Nazario低于Robust |
| Qwen 9B non-thinking | **2/2** | 2/2 | 0/2 | recall强增益，control FPR trade-off |
| Qwen 9B thinking | 2/2（均不显著） | 2/2 | 0/2 | reasoning后边际增益消失 |
| Qwen 35B non-thinking | 1/2 | 2/2 | 1/2 | PF持平，Nazario正向 |
| Qwen 35B thinking | 0/2 | 2/2 | 0/2 | recall饱和且FPR升高 |

跨16个“配置×数据集”单元：

- Ours的clean precision全部满足2pp非劣界值；
- Ours在7/16单元中attacked recall数值最高，但相对Robust显著胜出的只有3个单元：
  Pro non-thinking/PhishFuzzer，以及Qwen 9B non-thinking的两个数据集；
- Flash/PhishFuzzer的两个模式中，Robust显著胜过Ours；
- control FPR未通过2pp界值的7个单元全部来自Qwen，本地小模型更容易把“检测到注入”
  与“邮件是phishing”耦合。

因此H1得到**有条件、跨模型支持**，H2的clean部分得到完整支持，control FPR部分显示明确的
模型依赖trade-off。

## 注入检测

Ours injection-detection F1范围为`.9916--.9977`，所有模型、模式和数据集都接近满分。
这说明不同方法的最终差异不来自“是否发现注入”，而来自检测注入之后如何完成基础phishing
分类，以及是否把注入存在本身错误地作为phishing证据。

## 输出Token对比

以下为两个数据集和三种条件加权后的平均总输出tokens；non-thinking中等于可见答案tokens，
thinking中包含reasoning与答案。

| 模型—模式 | Direct | Robust | Ours | Ours相对同模型non-thinking |
|---|---:|---:|---:|---:|
| Flash non-thinking | 8.0 | 8.0 | 32.6 | 1× |
| Flash thinking | 221.6 | 190.2 | 238.6 | 7.3× |
| Pro non-thinking | 8.2 | 8.3 | 38.7 | 1× |
| Pro thinking | 289.6 | 299.4 | 359.2 | 9.3× |
| Qwen 9B non-thinking | 7.1 | 7.0 | 36.2 | 1× |
| Qwen 9B thinking | 1812.5 | 1571.5 | 1881.0 | 51.9× |
| Qwen 35B non-thinking | 10.8 | 10.2 | 37.7 | 1× |
| Qwen 35B thinking | 1360.5 | 1441.8 | 2032.9 | 54.0× |

效率结论：

- DeepSeek reasoning较克制，约190--359输出tokens；Qwen reasoning约1,361--2,033，
  模型/服务实现差异很大。
- Non-thinking Ours一般只需约33--39 tokens。
- 在PhishFuzzer上，Qwen 9B non-thinking Ours与thinking Direct的attacked recall仅差
  .4pp，却节省约50倍输出tokens；Qwen 35B non-thinking Ours的有注入F1还略高于
  thinking Robust。
- Pro non-thinking Ours在PhishFuzzer上同时超过non-thinking Robust和thinking Direct的
  attacked recall，并显著少用tokens，是H3/H4最干净的支持案例。
- Qwen thinking采用递增预算补跑；表中不包含此前失败尝试的tokens，因此实际实验累计
  计算开销更高。

本地结果没有输入tokens、延迟、吞吐、能耗和货币成本，跨API/本地部署只能严谨比较输出
token量，不能比较完整墙钟或美元成本。

## `ours_no_summary`消融

消融仅在PhishFuzzer的Qwen矩阵中完成：

- 9B non-thinking：full将attacked recall从`.949`提高到`.961`，但control FPR从`.028`
  提高到`.039`；两项差异均显著。摘要带来recall/FPR权衡。
- 35B non-thinking：full/no-summary的attacked recall为`.977/.975`，control FPR
  `.012/.016`，均不显著。
- 两个thinking模型中，full/no-summary在clean、attacked和control上的配对差异均不显著。

短摘要不是跨模型、跨模式的必要组件；其可观察收益主要出现在9B non-thinking，同时增加
输出tokens和误报。若论文篇幅有限，应将其作为机制消融，而不是独立核心贡献。

## 总体结论

全部实验共同支持一个比“普遍优于Robust”更准确、也更可信的结论：

> Injection-first structured prompting能在不开启reasoning时稳定改善Direct的攻击鲁棒性，
> 并在部分模型上进一步显著超过通用Robust prompt；当基础模型、Robust prompt或reasoning
> 已具有很强的抗注入能力时，其边际收益趋于持平。方法以约33--39个输出tokens恢复了
> reasoning baseline的大部分鲁棒性，同时可能在部分Qwen模型上增加legitimate-control FPR。

最强的正面证据是DeepSeek Pro non-thinking与Qwen 9B non-thinking；Qwen 35B提供“接近
饱和时不退化”的证据；Flash和完整thinking结果则构成方法边界与trade-off证据。整体足以
支持方法合理性、跨模型有效性和效率动机，但不支持“所有模型上都显著优于Robust”的绝对
表述。

