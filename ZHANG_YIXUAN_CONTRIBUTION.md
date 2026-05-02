# Individual Final Report

## Nmae: Zhang Yixuan UID: 3036480141

According to the updated project plan table in the final report, I am responsible for:

- `R1` Real-world queue strategies research
- `R3` Modeling assumptions 
- `S2` Case study evaluations
- `W1` Project Plan 
- `W2` Group Final Report

## Contribution focus

My contribution to this project is mostly about establishing the theoretical foundation, modeling the problem, and conducting the data-science evaluation for our simulation.

The main goal of my work is to translate the real-world hospitality problem into a structured computing model, define its mathematical boundaries, and interpret the raw output data to reveal meaningful insights.

## Detailed contribution record

### 1. Real-world queue strategies research (R1)

Implemented in Part 2 of the Final Report.

Completed work:
- conducted a comprehensive survey of four existing queue management solutions: Single queue system, Size-based queue system, VIP or reservation priority queue system, and App-based virtual queueing system
- identified target scenarios and cited specific real-world examples for each strategy
- evaluated the key benefits of each approach
- analyzed the practical drawbacks of each system
- extracted the underlying assumptions for each strategy

### 2. Modeling assumptions (R3)

Implemented in Part 4 of the Final Report.

Completed work:
- established strict modeling assumptions to bridge the gap between reality and code
- listed the reason for each assumption
- explicitly documented the real-world limitations of each assumption to demonstrate critical thinking

### 3. Case study evaluations (S2)

Implemented in Part 5 of the Final Report.

Completed work:
- wrote comprehensive trade-off analyses for all selected simulation pairs
- analyzed Pairs 01 & 02: proved the mathematical advantage of fine-grained queue categorization
- analyzed Pairs 07 & 08: wrote deep-dive stress test evaluations on demand concentration (Burst vs. Trickle) and the systemic paralysis caused by 8-person outlier groups
- analyzed Pair 09: quantified the hidden opportunity cost of withholding reserved tables during quiet vs. peak windows
- wrote an overall conclusion including strengths, limitations and future improvement of the model

### 4. Project Plan (W1)

Implemented in Part 8 of the Final Reprot.

Completed work:
- designed the overall blueprint and scope of the project during the initial phase
- structured the detailed task breakdown for all group members
- organized the role assignments to distribute workloads fairly

### 5. Group Final Report (W2)

Implemented in Part 1 and Part 6 of the Final Report.

Completed work:
- defined the daily-life problem of restaurant queueing, explaining its significance and challenges
- explicitly described how our group modeled this chaotic physical environment into a structured computing problem 
- explained our system design, including the modular architecture and the core simulation engine
- clearly explained our two key functions: Standalone Diagnostic Run (for baseline evaluation) and Automated Paired Comparison (for A/B testing)

## Short conclusion

My contribution in this phase establishes the **theoretical foundation, modeling limits, and analytical evaluation** of the simulation system. 

By conducting background research, defining modeling assumptions, writing the comprehensive trade-off analyses, and structuring the final report, I successfully transformed our coding efforts into a complete data-science evaluation project.

## Personal Evaluation

**What worked well:**
I believe I performed well in translating a chaotic daily-life problem into a structured computing problem. The clear separation of duties between the coding team and myself worked exceptionally well.

**What did not work well (and how it was resolved):**
Initially, we struggled with our case studies. We planned 6 pairs, but we later considered that Pairs 03, 04, 05 and 06 lacked analytical depth. Furthermore, we faced a methodology conflict regarding whether changing "customer arrival patterns" violated the rule of varying exactly one setting. We successfully resolved this by clarifying with the Lecturer and restructuring our report to feature Pairs 01 and 02 as "core operational tests," and Pairs 07, 08, and 09 as advanced "demand-side stress tests." 

## Reflection

This project significantly deepened my understanding of computational thinking. I learned how incredibly difficult it is to translate messy, unpredictable human behaviors (like customers walking to tables or deciding to leave a queue) into rigid, discrete algorithmic rules. 

I also developed a much sharper critical eye for data. For example, I learned that a high "Table Utilization" rate is sometimes a false positive that actually indicates a severe system bottleneck rather than high efficiency. Navigating feedback from our Tutor and Lecturer taught me how to academically defend my analytical choices. I felt a strong sense of accomplishment when my theoretical assumptions (from R3) perfectly predicted the systemic breakdowns in our advanced stress tests.

## AI Report

I am documenting my usage of AI tools for the writing process.

- **AI Tool Used:** Perplexity AI (Gemini 3.1 Pro Thinking).
- **Prompts Used:** 
  - *"详细描述一下他们的coding是什么样一个逻辑 实现了哪些功能"*
  - *"case study的run simulation的结果是什么样的现在他们已经设计好了 这是casestudy文件夹里和readme"*
  - *"这是我们casestudy的readme 现在我要开始写S2 该从哪些角度分析trade-off和overall conclusion caseresult我都给你了"*
  - *"结构有点问题 第一部分是• For each pair: present metrics side-by-side, analyze trade-offs, discuss simulation limitations, and compare to real-world restaurant practice.
第二部分是 Write an overall conclusion: strengths of the simulation, at least 3 limitations, at least 2 directions for future improvement."*
  - *"我觉得这6个casestudy后面几个有点水 质量不太高 特别是第六个 你还有什么角度来做case study吗"*
  - *"我们的casestudy是不是不能完全support这个system的design 因为我们的系统除了compare还有单独的run simulation功能 readme里有么？"*
  - *"这四种排队模式他们的经典优缺点有哪些 前提假设是什么"*
  - *"对于我们这个项目 把实际问题转化成一个coding project的时候一般需要哪些model assumption"*
  - *"有什么理由吗"*
  - *"你看到我之前给你的casestudy的readme没 一共9个pair 但是实际的report中我们只分析了12789这5个高含金量的 这个过渡句怎么改 在哪里改 我发给过你我们的fianl report"*
  - *"这个system design是不是应该进行一点seperation描述 怎么seperate更科学呢"*
  - *"key functions是不是应该聚焦于我们这个项目的两大特征 一个是比较 一个是单独的simulation"*
