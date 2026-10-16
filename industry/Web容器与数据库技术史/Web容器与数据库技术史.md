# 中间件 Web 容器与数据库软件技术发展史

> 一份关于 Web 中间件（Web 容器 / Web 服务器 / 反向代理 / 服务代理）与数据库软件演进脉络的结构化技术史。
> 覆盖区间：1990 年代至今（CGI 时期 → 云原生与服务网格）。
> 数据说明：市场份额类数据均以「区间 / 排名 / 定性」呈现，并标注来源与统计时点；确切成因与年份以公开史料为准。

---

## 目录

[TOC]

---

## 1. 引言

Web 容器（Container）与数据库（DBMS）是「中间件」层中最核心、也最具历史纵深的两类软件。Web 容器负责把 HTTP 请求映射到应用逻辑并管理连接、线程与生命周期；数据库负责数据的持久化、查询与一致性。二者共同构成了从「静态网页」到「动态交互」再到「分布式云原生系统」的技术底座。

本报告的写作逻辑：

- **时间维度**：以「请求处理模型」的跃迁为主线——进程模型（CGI）→ 线程/进程模型（Apache + mod_*) → Servlet 规范与容器 → 事件驱动/异步非阻塞（Nginx、Node.js、Netty）→ 嵌入式与微服务 → 云原生与服务网格（Envoy / Istio）→ Serverless。
- **数据维度**：以「数据模型」的扩展为主线——关系型（RDBMS）→ 文档 / KV / 宽列 / 图 / 时序 → 多模型与向量（AI 时代）。
- **架构维度**：单体内核 → 分层 / 模块化 → 微服务 / 云原生 → Serverless 与存算分离。

---

## 2. 阶段划分总表（按时间顺序）

下表给出 Web 容器演进的六大阶段，标注起止年份、标志性事件与关键版本 / 规范节点（数据库领域的关键节点并入第 5 节时间线）。

| 阶段 | 起止年份 | 标志性事件 | 关键版本 / 规范节点 |
|---|---|---|---|
| 一、静态 Web 与 CGI 动态化 | 1993–1997 | CGI 出现，Web 从静态文档走向交互；Apache 接棒 NCSA httpd；LAMP 雏形 | CGI（NCSA，1993）；Apache HTTP Server（1995）；Servlet 1.0 / Java Web Server（1996–1997）；PHP（1995）；MySQL（1995）；PostgreSQL（1996） |
| 二、Servlet/JSP 规范确立与 Java 应用服务器 | 1997–2003 | Java 规范化为企业 Web 标准；商业应用服务器（WebSphere/WebLogic）与开源容器（Tomcat/Jetty/JBoss）并立 | Servlet 2.0–2.4（1997–2003）；JSP（1998）；Tomcat 3.0（1999，Servlet 2.2/JSP 1.1）；Tomcat 4.0 Catalina（2001）；WebSphere（1998）、WebLogic（1996/1998）、JBoss（1999） |
| 三、开源容器普及与高性能反向代理崛起 | 2003–2009 | 高并发（C10K）倒逼事件驱动架构；Nginx 以异步非阻塞模型颠覆 Apache 霸主地位；LAMP 与 Web 2.0 普及 | Apache 2.0/2.2（2002/2005）；Nginx 0.1.0（2004）；Lighttpd（2003）；Jetty 6 续体模型（2006）；Tomcat 5/6（2003/2006）；Resin（1999）；Ajax（2005） |
| 四、异步非阻塞与事件驱动范式 | 2009–2015 | 实时 / 长连接 / 移动场景成为常态；Reactor 模型主流化；HTTP/2 与 WebSocket 落地 | Node.js（2009）；Servlet 3.0 异步（2009）；Jetty 7/8 WebSocket（2009–2010）；Netty 4（2013）；Undertow（2013）；Nginx Plus（2013）；HTTP/2（2015） |
| 五、嵌入式容器与微服务 | 2013–2018 | 容器化（Docker/K8s）与 DevOps 推动「应用自带容器」；微服务拆分单体 | Spring Boot（2014，内嵌 Tomcat/Jetty/Undertow）；Docker（2013）；Kubernetes（2014）；WildFly 8 默认 Undertow（2014）；微服务架构流行 |
| 六、云原生、服务网格与 Serverless | 2016–至今 | K8s 成为事实标准；Sidecar 代理接管东西向流量；函数即服务（FaaS）兴起；Java 进入 Jakarta EE 时代 | Envoy（2016，Lyft）；Istio（2017）；Knative / Serverless（2018+）；Jakarta EE 9（jakarta.* 命名空间，2020）、10（2022）、11（2024）；Tomcat 10/11（2020/2024）；Quarkus / Micronaut（云原生 Java） |

---

## 3. 各阶段深入分析

### 3.1 阶段一：静态 Web 与 CGI 动态化（1993–1997）

**背景与驱动因素**
- 硬件：单核低主频 CPU、内存以兆计，网络以拨号 / 低速专线为主；并发量极低。
- 需求：Web 由「只读静态文档」走向「表单提交、查询、会话」等交互需求。
- 生态：NCSA 发布 Mosaic 浏览器（1993），Web 用户快速膨胀。

**代表性理论与模型**
- **C/S（客户端 / 服务器）** 萌芽，**B/S（浏览器 / 服务器）** 模式确立。
- **CGI（通用网关接口）进程模型**：每请求一进程（fork-exec），通过环境变量 + 标准 I/O 与 Web 服务器通信。

**关键技术与系统**
- NCSA httpd 与 CGI（1993，NCSA）；Apache HTTP Server（1995，由 Apache 小组基于 NCSA httpd 重写）。
- 脚本语言：Perl（CGI 主力）、PHP（1995，初为 CGI 形态）、Python（1991）。
- 数据库：MySQL（1995）、PostgreSQL（1996）开源关系型数据库登场，与 PHP/Apache 构成 LAMP 雏形。

**局限**：CGI「每请求一进程」在并发上升时进程创建 / 销毁开销成为瓶颈，催生了进程内模块（mod_perl、mod_php）与 FastCGI（1996）。

### 3.2 阶段二：Servlet/JSP 规范确立与 Java 应用服务器（1997–2003）

**背景与驱动因素**
- Java 凭借「一次编写，到处运行」与强类型企业特性，成为大型组织后端首选。
- 需要一种跨厂商、标准化的服务端 Java 组件模型来替代各家的私有 CGI/ISAPI 方案。

**代表性理论与模型**
- **B/S + 分层架构（MVC）**：Servlet 处理请求控制，JSP 负责视图，EJB/业务层负责模型。
- **J2EE 平台化**：将 Web、事务、消息、目录等能力标准化。

**关键技术与系统**
- **Servlet 规范**：1.0（1997）由 Sun 的 Pavni Diwanji 制定；2.0（1997）、2.1（1998）、2.2（1999，纳入 J2EE、引入 .war 独立 Web 应用）、2.3（2001，引入 Filter）、2.4（2003，web.xml 改用 XML Schema）。
- **JSP**：1998 年随 J2EE 1.2 推出，与 Servlet 配合形成「Model 2」MVC。
- **开源容器**：Tomcat 3.0（1999，James Duncan Davidson 基于 Sun 代码捐赠 ASF，实现 Servlet 2.2/JSP 1.1）；Jetty（1995 起，Mort Bay，后 2009 入 Eclipse）。
- **商业应用服务器**：IBM WebSphere（1998 起）、BEA WebLogic（1996 起，2008 年被 Oracle 收购）、JBoss（1999 起，2006 被 Red Hat 收购）、Caucho Resin（1999）。

**意义**：Servlet 容器把「连接管理 + 线程池 + 生命周期」从应用代码中剥离，确立了现代 Web 容器的核心契约（init / service / destroy）。

### 3.3 阶段三：开源容器普及与高性能反向代理崛起（2003–2009）

**背景与驱动因素**
- **C10K 问题**：单服务器需同时维持上万并发连接，Apache 的「每连接一进程/线程」模型内存与上下文切换成本过高。
- **Web 2.0 与 Ajax（2005）**：页面局部刷新、富交互带来请求量激增。
- 硬件：多核 CPU 普及，但操作系统仍多以阻塞 I/O 为主，需要新的 I/O 编排方式。

**代表性理论与模型**
- **事件驱动 / 异步非阻塞（Reactor）**：单线程事件循环 + epoll/kqueue，用极少线程支撑海量连接。
- **反向代理 / 负载均衡**：把静态资源、SSL 终结、缓存前置到应用服务器之前。

**关键技术与系统**
- **Nginx**（0.1.0，2004-10-04，Igor Sysoev，为 Rambler 解决高并发）：BSD 许可，事件驱动，迅速成为反向代理 / 负载均衡 / 静态服务事实标准；Nginx, Inc.（2011）成立，2019 被 F5 收购。
- **Apache 2.x**：引入 Worker / Event MPM，向异步化靠拢（Event MPM 在 2.4 成为默认）。
- **Lighttpd（2003）**、**Cherokee** 等同代事件驱动服务器。
- Tomcat 5（Servlet 2.4/JSP 2.0，2003）、Tomcat 6（Servlet 2.5，2006）；Jetty 6（2006，续体 continuations 支持异步）。

### 3.4 阶段四：异步非阻塞与事件驱动范式（2009–2015）

**背景与驱动因素**
- 实时应用（聊天、推送、行情）、移动端、长连接（WebSocket）成为主流。
- 微服务萌芽，对「高吞吐、低尾延迟」的网络层提出更高要求。

**代表性理论与模型**
- **Reactor / Proactor 全异步 I/O**；**Servlet 3.0 异步处理**；**WebSocket 全双工**；**HTTP/2 多路复用**。
- 语言级事件循环：Node.js 将「前端 JS」带入服务端，验证单线程事件循环的高吞吐可能。

**关键技术与系统**
- **Node.js（2009，Ryan Dahl）**：基于 V8 + 事件循环，非阻塞 I/O，催生 Express / Koa 等框架与全栈 JS。
- **Servlet 3.0（2009）**：规范级异步 Servlet，容器可异步处理请求。
- **Jetty 7/8（2009–2010）**：WebSocket、SPDY 支持；**Netty 4（2013）**：Trustin Lee 创建的 Reactor 网络框架，成为 Kafka、Cassandra、Dubbo、gRPC 等基础设施的通信底座。
- **Undertow（2013，Red Hat）**：为 WildFly 8（2014）打造的轻量非阻塞 Web 服务器，可处理十万级并发。
- **HTTP/2（2015，RFC 7540）**：多路复用、头部压缩，Nginx 1.9.5 起原生支持。
- **Nginx Plus（2013）**：商业版引入高级负载均衡与可观测指标。

### 3.5 阶段五：嵌入式容器与微服务（2013–2018）

**背景与驱动因素**
- **Docker（2013）/ Kubernetes（2014）** 让「应用 + 运行时」打包为不可变镜像，传统「先装应用服务器再部署 war」的运维模式被颠覆。
- **DevOps / CI-CD** 要求应用自包含、启动快、可水平扩展。

**代表性理论与模型**
- **微服务**：单体拆分为小而独立的服务，每服务自带嵌入式运行时。
- **嵌入式容器**：容器作为库（library）嵌入应用，而非应用部署进容器。

**关键技术与系统**
- **Spring Boot（2014）**：默认内嵌 Tomcat，可选 Jetty / Undertow，使「java -jar 即服务」成为常态。
- **WildFly 8（2014）**：以 Undertow 取代 JBossWeb 作为默认 Web 服务器，并能直接作为非阻塞反向代理，减少 Apache/Nginx 前置依赖。
- **云厂商 PaaS**：AWS Elastic Beanstalk、Heroku、Cloud Foundry 等将容器运行时托管化。

### 3.6 阶段六：云原生、服务网格与 Serverless（2016–至今）

**背景与驱动因素**
- K8s 成为调度标准；服务数量爆炸，东西向（服务间）流量治理需求压过南北向（入口）。
- **Service Mesh** 用 Sidecar 代理把熔断、重试、mTLS、可观测性从应用下沉到基础设施层。
- **Serverless / FaaS**：用户只关心函数，运行时与扩缩容完全托管。

**代表性理论与模型**
- **数据面 / 控制面分离**：xDS 动态配置（LDS/RDS/CDS/EDS），配置热更新无需 reload。
- **Sidecar 代理 + 服务网格（Istio + Envoy）**；**存算分离**；**函数即服务**。

**关键技术与系统**
- **Envoy（2016-09-14 开源，Lyft，Matt Klein）**：C++ 编写、为高并发低尾延迟设计，原生可观测（logs/metrics/tracing），2017 年捐献 CNCF；成为 Istio 默认数据面。
- **Istio（2017）**：以 Envoy 为数据面，提供流量管理、安全与可观测。
- **Knative / OpenFaaS / AWS Lambda / 阿里云函数计算**：Serverless 运行时。
- **Jakarta EE 转型**：Java EE 移交 Eclipse 基金会后，包名由 `javax.*` 改为 `jakarta.*`（Jakarta EE 9，2020；10，2022；11，2024）；Tomcat 10（2020）/11（2024）跟进。
- **云原生 Java**：Quarkus、Micronaut 面向 GraalVM 原生镜像与极低启动时间，契合 Serverless。

---

## 4. 对比与演进脉络

### 4.1 各类容器 / 模型的定位对比

| 模型 / 容器 | 定位 | 并发模型 | 部署方式 | 性能特征 | 适用场景 |
|---|---|---|---|---|---|
| CGI | 最早的动态网关 | 每请求一进程（fork-exec） | 独立可执行 + Web 服务器 | 吞吐低、开销大 | 历史交互页面（已淘汰） |
| 模块内嵌（mod_php / ISAPI / mod_perl） | 进程内脚本执行 | 线程 / 进程内 | 编译进 Apache/IIS | 中，依赖宿主 MPM | LAMP、Windows/.NET 传统站点 |
| Servlet 容器（Tomcat/Jetty/Undertow） | Java Web 运行时 | 线程池 + 异步 Servlet | 独立服务 或 嵌入式 | 中高，稳定成熟 | Java EE / Spring 企业应用 |
| Nginx / OpenResty | 反向代理 / 静态 / API 网关 | 事件驱动、异步非阻塞 | 独立进程（常前置） | 极高并发、低内存 | 高并发入口、负载均衡、网关 |
| Netty | Reactor 网络框架（非完整容器） | 事件驱动、全异步 | 作为库嵌入应用 | 极高吞吐、低尾延迟 | RPC/消息/代理底层通信 |
| Node.js | JS 运行时 + 内置容器 | 单线程事件循环 | 独立进程 | 高 I/O 并发 | 实时 API、BFF、全栈 JS |
| Envoy | 云原生 L7 服务代理 | 多线程事件循环 + 线程本地存储 | Sidecar / 边缘 | 高吞吐、低尾延迟、强可观测 | 服务网格数据面、入口网关 |
| Serverless / FaaS | 函数运行时（托管） | 平台托管、按请求扩缩 | 完全托管、无服务器 | 冷启动敏感、按需计费 | 事件驱动、突发、轻量后端 |

### 4.2 数据模型的演进

| 数据模型 | 代表产品（首现年份） | 核心数据模型 | 典型场景 | 优势 | 短板 |
|---|---|---|---|---|---|
| 关系型（RDBMS） | Oracle（1979）、MySQL（1995）、PostgreSQL（1996）、SQL Server（1989） | 二维表 + SQL + ACID | 交易、账务、ERP | 强一致、成熟生态 | 水平扩展难、schema 变更重 |
| 文档型 | MongoDB（2009）、CouchDB（2005） | JSON/BSON 文档 | 内容、目录、灵活 schema | schema 灵活、易水平扩展 | 多文档事务弱、联表弱 |
| 键值型（KV） | Redis（2009）、Memcached（2003）、DynamoDB（2012） | key→value | 缓存、会话、排行榜 | 极速、简单 | 仅按 key 查、无复杂查询 |
| 宽列（Wide-Column） | Cassandra（2008）、HBase（2008） | 列族 / 有序列 | 海量写入、时序、IoT | 线性扩展、高可用 | 查询受限、运维复杂 |
| 图（Graph） | Neo4j（2007） | 节点-边-属性 | 社交、知识图谱、风控 | 多跳关系高效 | 超大图扩展性受限 |
| 时序（Time-Series） | InfluxDB（2013）、TimescaleDB（2015）、Prometheus（2015） | 时间戳为主键 | 监控、指标、传感器 | 高压缩、时序聚合 | 通用事务弱 |
| 分析型 / 列存 OLAP | ClickHouse（2016）、Vertica、Greenplum | 列存 + 向量化 | 实时分析、BI、日志 | 极速扫描聚合 | 写入/更新模型特殊 |
| 向量 / 多模型（AI 时代） | Milvus（2019）、pgvector（PostgreSQL 扩展）、Redis Vector | 高维向量 + ANN | 检索增强（RAG）、相似度 | 支撑 AI 语义检索 | 依赖近似算法、精度权衡 |

**演进主线**：关系型（一致性优先）→ NoSQL 多样化（规模 / 灵活优先）→ NewSQL / 多模型（兼顾事务与扩展）→ 向量与 AI（语义优先）。

### 4.3 整体架构路径

| 架构阶段 | 典型形态 | 容器 / 数据特征 | 代表技术 |
|---|---|---|---|
| 单体内核 | 单进程 / 单机数据库 | CGI、单实例 RDBMS | Apache+mod_php、MySQL 单机 |
| 分层 / 模块化 | 应用服务器 + 连接池 + 主从库 | Servlet 容器、读写分离 | Tomcat + 连接池、MySQL 主从 |
| 微服务 / 云原生 | 多服务 + 容器编排 + 分片/副本 | 嵌入式容器、服务网格、分片 | Spring Boot + K8s + Envoy、MongoDB 分片、Cassandra 多 DC |
| Serverless / 存算分离 | 函数 + 托管存储 + 弹性计算 | 托管运行时、对象存储、计算存储解耦 | AWS Lambda、Aurora Serverless、Snowflake、存算分离数仓 |

### 4.4 云原生、容器化、AI 基础设施对未来的影响

- **容器化**：运行时被「库化 / 镜像化」，传统重型应用服务器退居后台，轻量容器（Tomcat 嵌入式、Netty、Envoy）成为默认。
- **云原生**：控制面与数据面分离、声明式配置（xDS）、可观测内建，成为中间件标配。
- **AI 基础设施**：向量检索、GPU 调度、推理网关、RAG 流水线催生「AI 网关」「推理代理」新一层；Web 容器从「转发 HTTP」延伸到「编排模型调用、限流、缓存 Embedding」。

---

## 5. 关键节点时间线（年份 — 事件）

> 合并 Web 容器与数据库两条主线；来源见第 8 节。

**1990 年代**

- 1991 — HTTP/0.9 出现；Tim Berners-Lee 发明 WWW。
- 1993 — NCSA 制定 **CGI**；Mosaic 浏览器发布；NCSA httpd。
- 1994 — W3C 成立；SSL 出现（网景）。
- 1995 — **Apache HTTP Server** 诞生（基于 NCSA httpd）；**MySQL** 发布；**PostgreSQL**（POSTGRES 开源化）；**PHP** 诞生；**JavaScript** 诞生；**Java** 发布；IIS 1.0（随 NT 3.51）。
- 1996 — **Servlet 1.0**（Sun）；**HTTP/1.0**（RFC 1945）；**FastCGI**（Open Market）；**WebLogic** 初版；IIS 2.0（NT 4.0）；Redis 前身尚早。
- 1997 — **Servlet 2.0**；**Java Web Server** 正式产品化；**HTTP/1.1**（RFC 2068）。
- 1998 — **JSP** 随 J2EE 1.2 推出；**IBM WebSphere** 应用服务器发布；**Resin**（Caucho）诞生。
- 1999 — **Tomcat 3.0**（Servlet 2.2/JSP 1.1，ASF）；**JBoss** 开源；**Servlet 2.2** 纳入 J2EE。

**2000 年代**

- 2001 — **Tomcat 4.0 Catalina**（Servlet 2.3，引入 Filter）；**Servlet 2.3**。
- 2003 — **Apache 2.0**；**Servlet 2.4**（XML Schema）；**Lighttpd** 发布；**HBase** 思路源于 Google BigTable 论文（2006 正式立项，2008 发布）。
- 2004 — **Nginx 0.1.0**（10 月 4 日）；**Apache 2.2**；**Jetty** 进入 Codehaus 时代；**Facebook** 大规模使用 MySQL。
- 2005 — **Servlet 2.5**；**Ajax** 普及；**Apache Cassandra** 由 Facebook 开发（2008 开源）。
- 2006 — **HTTP/1.1** 巩固；**Apache Hadoop** 发布（HBase 随之）；Jetty 6 续体模型；**Google Bigtable** 论文影响。
- 2007 — **Neo4j** 发布；**Servlet 3.0** 草案；**Android** 发布（间接推动移动 Web）。
- 2008 — **Apache Cassandra** 开源并进入 Apache；**HBase** 成为 Apache 顶级项目；**Node.js** 尚未出（2009）。
- 2009 — **Servlet 3.0**（异步 Servlet）；**Node.js**（Ryan Dahl）；**MongoDB** 发布；**Redis** 发布（Salvatore Sanfilippo）；Jetty 7/8（WebSocket/SPDY）。

**2010 年代**

- 2010 — **Elasticsearch** 发布；**Servlet 3.0** 落地；**Nginx, Inc.** 成立（2011）。
- 2011 — **Nginx 1.0.0** 稳定版；**OpenResty**（基于 Nginx + LuaJIT，agentzh）发布；**Apache 2.4**（Event MPM 默认化）；**Nginx 商业公司**成立。
- 2012 — **Kubernetes** 前身（Borg 论文）；**Apache 2.4** 广泛部署；**TimescaleDB** 思路；**Docker** 尚未出（2013）。
- 2013 — **Docker** 发布；**Servlet 3.1**（非阻塞 I/O、HTTP Upgrade）；**Netty 4**；**Undertow** 项目启动（Red Hat）；**Nginx Plus**；**InfluxDB** 发布；**Cassandra** 生产成熟。
- 2014 — **Kubernetes** 开源（Google）；**Spring Boot** 发布（内嵌容器）；**WildFly 8** 默认 Undertow；**HTTP/2** 标准化（RFC 7540）。
- 2015 — **Envoy** 于 Lyft 启动开发（5 月）；**HTTP/2** 正式；**CockroachDB** 发布（NewSQL）；**Prometheus** 发布。
- 2016 — **Envoy 开源**（9 月 14 日）；**ClickHouse** 开源（Yandex）；**HTTP/3/QUIC** 起步；**Istio** 酝酿。
- 2017 — **Istio** 发布；**Envoy 捐献 CNCF**；**Servlet 4.0**（HTTP/2）。
- 2018 — **Knative / Serverless** 生态成形；**云原生数据面** 普及。
- 2019 — **F5 收购 Nginx**（6.7 亿美元）；**Milvus** 向量数据库发布；**Redis 许可变更** 引发社区关注；**Jakarta EE** 过渡。

**2020 年代**

- 2020 — **Jakarta EE 9**（`jakarta.*` 命名空间）；**Tomcat 10.0**；**Valkey** 尚未分叉（2024）。
- 2021 — **Nginx 在 W3Techs 份额反超 Apache** 并持续领先（约 2021 起）。
- 2022 — **Jakarta EE 10**；**Tomcat 10.1**；**Igor Sysoev 离开 Nginx/F5**；**Valkey** 分支酝酿。
- 2023 — **Jetty 12** 发布；**Tomcat 11** 路线；向量检索进入主流 RDBMS（pgvector 流行）。
- 2024 — **Jakarta EE 11 / Servlet 6.1**；**Tomcat 11.0**；**Redis 7.4 许可变更**，Linux 基金会 **Valkey** 分叉；**Serverless + AI 网关** 成为热点。
- 2026 — 现状：Nginx 约占已知 Web 服务器的 ~32%（W3Techs，2026-06）；Oracle/MySQL/PostgreSQL 仍居 DB-Engines 前三（详见第 6 节）。

---

## 6. 现状对比调研

> 市场份额均标注来源与统计时点；产品体系与版本以公开信息为准。Web 服务器份额数据来自 W3Techs（2026-06 概览）[参考 W3]；数据库排名来自 DB-Engines（2026-06/08）[参考 DB]。

### 6.1 Web 容器 / 服务器现状对比

| 产品 | 所属公司 / 社区 | 定位与目标场景 | 市场份额 / 使用概况 | 产品体系（版本与生态） | 技术架构要点 | 当前主流架构与未来演进 |
|---|---|---|---|---|---|---|
| **Apache Tomcat** | Apache 软件基金会 | 轻量 Servlet/JSP 容器，Java Web 标准实现 | 广泛用于 Java 应用；W3Techs 将其计入「<0.1%」独立 Web 服务器（常作应用服务器而非前置） | Tomcat 9（Java EE 8，2027-03 止维护）、10.1（Jakarta 10）、11（Jakarta 11，2024） | Catalina 容器 + Coyote 连接器（NIO/APR），线程池 | 嵌入式（Spring Boot）为主；向 Jakarta EE 11、HTTP/3 演进 |
| **Eclipse Jetty** | Eclipse 基金会 | 可嵌入、轻量、高性能 Servlet 容器 | 大量嵌入框架（Spark、ActiveMQ、Google App Engine 早期）；同属小份额独立服务器 | Jetty 9.4（LTS）、10/11、12（2023，模块化 Handler API） | 异步 Handler、低内存、WebSocket/HTTP2 原生 | 模块化 Handler 架构；云原生嵌入与 GraalVM 原生镜像 |
| **Undertow** | Red Hat / JBoss | 高性能非阻塞 Web 服务器，WildFly 默认 | 主要随 WildFly/SpringBoot 使用；独立份额小 | 随 WildFly 8+ 内置；支持 Servlet 4、HTTP/2、SPDY | XNIO 非阻塞 I/O，Jar < 4MB，阻塞/非阻塞双模式 | 继续作为 WildFly 与嵌入式首选；与云原生 Java 协同 |
| **Netty** | Netty 项目（原 JBoss/Red Hat） | Reactor 网络框架（非完整 Web 容器） | 基础设施级：Kafka、Cassandra、Dubbo、gRPC、Elasticsearch 底层 | Netty 4.x（2013 起）、5.x 实验；大量子模块 | 事件循环 + 零拷贝 + 池化 Buffer | 持续支撑云原生中间件通信；关注 Native 传输（io_uring/epoll）与 HTTP/3 |
| **Nginx** | F5（原 Nginx, Inc.） | 反向代理 / 负载均衡 / 静态 / API 网关 | **W3Techs 2026-06：约 31.9%**（已知站点第一）；高流量站更强 | 开源 Nginx + Nginx Plus（商业）；1.29/1.31 主线、稳定 1.28+ | 事件驱动、epoll/kqueue、单 worker 高并发 | 强化 HTTP/3、API 网关、边缘；受 Valkey 同类分叉（开源治理）影响有限 |
| **OpenResty** | OpenResty（agentzh / 春哥）社区 | 基于 Nginx + LuaJIT 的可编程网关 | 国内外网关 / 边缘逻辑热门（API 网关、WAF） | OpenResty 主线（基于 Nginx 1.2x）+ Lua 生态（lua-resty-*） | Nginx 事件模型 + 嵌入式 LuaJIT | 继续主导可编程网关；与 APISIX（基于 Nginx/OpenResty）生态竞争 |
| **Envoy** | CNCF（原 Lyft） | 云原生 L7 服务代理 / 数据面 | W3Techs 2026-06：约 1.2%；服务网格事实标准 | Envoy 主线 + Istio/APISIX/Ambassador 等构建于其上 | C++ 多线程 + xDS 动态配置 + 原生可观测 | 服务网格与入口网关核心；与 WASM 扩展、eBPF 融合 |
| **Microsoft IIS** | 微软 | Windows 集成 Web 服务器 / ASP.NET 平台 | W3Techs 2026-06：约 3.2%；Windows 企业内网主流 | IIS 10（Win Server 2016/2019/2022），随 Windows 生命周期 | 模块化（40+ 模块）、集成管道、应用池隔离 | 随 Windows 生态；.NET 云（Azure App Service）承接新负载 |
| **云厂商服务**（如 AWS ALB/API GW、Lambda、Azure App Service、函数计算） | AWS / Azure / 阿里云等 | 全托管入口、网关、Serverless 运行时 | 企业上云首选；与自建 Nginx/Envoy 互补 | ALB、API Gateway、CloudFront、Lambda、Elastic Beanstalk、函数计算、APISIX 托管版 | 托管控制面 + 多租户数据面 + 存算分离 | 进一步托管化、按量计费、内置 AI 网关与安全防护 |

### 6.2 数据库现状对比

| 产品 | 所属 / 社区 | 定位与目标场景 | 市场份额 / 使用概况（DB-Engines 2026-06/08） | 产品体系（版本与生态） | 技术架构（存储 / 计算 / 复制高可用） | 当前主流架构与未来演进 |
|---|---|---|---|---|---|---|
| **MySQL** | Oracle（开源） | 通用关系型、Web/交易首选 | DB-Engines 第 2（得分 ~842–856，同比下降）；开源关系型标杆 | 8.4 LTS + 9.0 Innovation 双轨；MariaDB 分支；Percona 发行版 | InnoDB 行存 + 缓冲池；主从 / 组复制（MGR）；读写分离 | 云托管（RDS/Aurora）、存算分离（Aurora）、HTAP 试探；受 PostgreSQL 替代压力 |
| **PostgreSQL** | 开源社区 | 标准兼容、可扩展关系型 + 多模型 | DB-Engines 第 4（得分 ~684–688，**同比唯一双增长**）；开发者口碑领先 | 16/17/18 主线；扩展生态（PostGIS、TimescaleDB、Citus、pgvector） | 堆表 + MVCC + WAL；流复制 / 逻辑复制；共享存储扩展 | 多模型（JSONB/图/时序/向量）、分布式（Citus）、云原生（Aurora PostgreSQL、Cloud SQL） |
| **Oracle Database** | Oracle | 企业级关系型 + 多模型 | DB-Engines 第 1（得分 ~1123，但同比下降明显） | 23ai/23c（集成 AI Vector、Property Graph） | RAC、ASM、多模型；成熟备份/容灾 | 自治数据库（Autonomous DB）、AI 向量与图、云化（OCI） |
| **MongoDB** | MongoDB, Inc. | 文档型（JSON/BSON） | DB-Engines 第 5（得分 ~385）；文档库绝对领先 | 社区版 + Atlas 云服务；7.x | WiredTiger 存储；副本集 + 分片；多文档事务 | Atlas 多云、向量搜索、Serverless、与 AI/RAG 深度整合 |
| **Redis** | Redis Ltd.（开源社区 + Valkey 分叉） | 内存 KV / 数据结构缓存 | DB-Engines 第 8（得分 ~150–157，KV 第一） | Redis 7.x + 模块（RediSearch/JSON/TimeSeries）；Valkey 分叉（2024） | 内存 + 可选持久化（AOF/RDB）；主从 + 哨兵 + 集群 | 实时缓存/队列/排行榜；向量检索；**2024 许可变更引发 Valkey 分叉**；云托管（ElastiCache/内存版） |
| **Apache Cassandra** | Apache（DataStax 等商业） | 宽列、海量写入、多 DC 高可用 | DB-Engines 第 10（得分 ~100）；宽列第一 | 4.x/5.x；DataStax Astra DB；ScyllaDB 兼容替代 | LSM-Tree + 无主多副本（可调一致性）；线性扩展 | 多活、全球分布；受 ScyllaDB（C++/无 GC）竞争；云托管（Astra） |
| **ClickHouse** | ClickHouse Inc.（开源，原 Yandex） | 列存 OLAP / 实时分析 | DB-Engines 第 26（得分 ~25，但同比涨幅显著） | 开源 + ClickHouse Cloud；24/25 主线 | 列存 + 向量化执行 + 物化视图；分片副本 | 实时数仓、日志/指标分析；云原生存算分离；与 OLAP 竞争（Doris/StarRocks） |
| **Neo4j** | Neo4j, Inc. | 原生图数据库 | DB-Engines 图库第 1（总榜 ~第 20，得分 ~49） | 社区/企业版；5.x；Cypher 查询语言 | 原生图存储 + 索引；因果集群（因果一致性） | 知识图谱、风控、欺诈检测；与 GNN/AI 结合；云托管（Aura） |
| **Apache HBase** | Apache（基于 Hadoop/HDFS） | 宽列、海量稀疏数据、近实时读写 | 总榜 ~第 40+（得分 ~9–10）；Hadoop 生态内厚 | 2.x/3.x；依赖 HDFS + ZooKeeper | LSM + HDFS 持久化；Region 分裂 + 副本；强一致行级 | 与 Hadoop/Spark 协同的大数据湖仓；云托管（EMR/DataHub）；受 Cassandra/云服务替代压力 |

> 说明：DB-Engines 分数衡量「流行度」（搜索、讨论、岗位等），并非装机量；具体数值每月浮动，参见 [参考 DB]。Web 服务器份额为「已知 Web 服务器站点占比」，且一站点可能使用多个服务器（W3Techs，2026-06）[参考 W3]。

---

## 7. AI 时代 Web 容器的发展方向研判

1. **从「转发流量」到「编排智能」**：Web 容器不再只转发 HTTP，而将内建「模型调用编排」——请求路由到不同模型、Token 限流、Prompt 缓存、RAG 检索前置、推理结果流式回传（SSE/HTTP 流）。「AI 网关 / 推理代理」成为新的一层（基于 Envoy、APISIX、Nginx 的可编程能力）。
2. **长连接与流式成为常态**：大模型对话天然是 SSE / 流式响应，对容器的「异步非阻塞、背压、超时与熔断」要求更高；Netty/Envoy 类 Reactor 模型比传统线程池模型更契合。
3. **Serverless + GPU 弹性**：函数计算与「按需 GPU」结合，Web 容器需要极低冷启动（GraalVM 原生镜像、Quarkus/Micronaut），并能在请求到达时秒级拉起含推理能力的运行时。
4. **向量与语义路由下沉到数据/网关层**：pgvector、Redis Vector、Milvus 让「语义检索」成为标准能力；Web 容器可能承担 Embedding 缓存与语义缓存（Semantic Cache），降低推理成本。
5. **可观测与安全的「AI 化」**：Sidecar（Envoy）天然可采集全链路追踪，AI 时代将扩展到「Prompt/Token 成本、幻觉率、模型版本灰度」；mTLS 与内容安全过滤前置到网格层。
6. **多模型与多云路由**：企业常同时接多家大模型，Web 容器承担「模型抽象层」——统一协议、故障转移、成本最优路由，类似服务网格对多版本服务的流量治理。
7. **边缘 AI 推理**：Nginx/OpenResty/Envoy 在边缘节点承担轻量推理与缓存，配合端侧小模型，形成「云-边-端」推理分层。

**结论**：Web 容器的核心契约（连接管理、并发模型、生命周期）不变，但「职责面」从「协议转发」扩展到「智能编排」；事件驱动/异步非阻塞架构（Nginx、Netty、Envoy）与云原生托管（Serverless、服务网格）将持续主导，传统重型 Servlet 容器更多退居为「应用内嵌运行时」。

---

## 8. 参考文献与引用来源

> 以下为本报告撰写过程中核验与引用的公开资料（访问时点：2026-10）。年份、版本与规范节点以各原始来源为准。

**Web 容器 / 服务器**
- [W3] W3Techs — Web Server Market Share（2026-06 概览）：<https://w3techs.com/technologies/overview/web_server>
- [NGX] Nginx — Wikipedia / 历史与份额：<https://wiki2.org/en/Nginx> ；Nginx 历史：<https://wiki.linux-server-admin.com/software/webserver/nginx/history>
- [CGI] Server application programming interface（CGI/ISAPI/FastCGI 历史）：<https://grokipedia.com/page/Server_application_programming_interface>
- [SERV] Jakarta Servlet 版本史（Servlet 1.0–6.1）：<https://wikiwand.com/en/Java_Servlet>
- [TOM] Apache Tomcat 历史：<https://wiki.linux-server-admin.com/software/application-server/apache-tomcat/history> ；官网：<https://tomcat.apache.org/>
- [JET] Eclipse Jetty（历史与版本）：<https://www.wikiwand.com/en/articles/Eclipse_Jetty>
- [UND] Undertow 使用详解（Red Hat/JBoss，WildFly 8 默认）：<https://blog.csdn.net/zhangzehai2234/article/details/136033744> ；WildFly 8 访谈：<https://www.infoq.com/news/2014/02/wildfly8-interview/>
- [ENV] Envoy joins the CNCF（Lyft，Matt Klein）：<https://eng.lyft.com/envoy-joins-the-cncf-dc18baefbc22> ；Envoy 云原生解读：<https://myf5.net/post/2947.htm>
- [IIS] 微软 IIS 生命周期与技术沿革：<https://learn.microsoft.com/zh-cn/lifecycle/products/internet-information-services-iis> ；百科：<https://baike.baidu.com/item/%E5%9B%A0%E7%89%B9%E7%BD%91%E4%BF%A1%E6%81%AF%E6%9C%8D%E5%99%A1/18151753>
- [NODE] Node.js（事件循环、2009）：<https://nnkksolution.in/blog/frontend-vs-backend-vs-full-stack-development-explained>

**数据库**
- [DB] DB-Engines Ranking（流行度排名，2026-06/08）：<https://db-engines.com/en/ranking> ；趋势：<https://db-engines.com/en/ranking_trend>
- [DBT] 数据库时间线（Oracle/MySQL/PostgreSQL/MongoDB/Redis/Cassandra/HBase 等）：<https://webref.lukasmurdock.com/databases>
- [OP100] BenchCouncil Open100（开源数据库与中间件作者/年份）：<https://www.benchcouncil.org/evaluation/opencs>
- [ENM] 墨天轮 — 十大主流 DBMS（发行时间/模型）：<https://cs.enmotech.com/db/208808>
- [CSDN-DB] 数据库发展史综述（层次/关系/NoSQL/NewSQL）：<https://blog.csdn.net/weixin_52174724/article/details/151367081>
- [QQ-DB] 数据库模型演进（文档/KV/图/时序/向量）：<https://news.qq.com/rain/a/20241012A01CKH00>

**协议 / 通用**
- [HTTP] HTTP/0.9–HTTP/3 历史脉络（Web 发展史）：<https://blog.csdn.net/zp2605811855/article/details/89048146>
- [W3C] World Wide Web Consortium：<https://www.w3.org/>

> 注：部分市场份额（如 Redis 许可变更、Valkey 分叉、各产品具体得分）随时间变动较快，引用时请以 DB-Engines、W3Techs 当期官方数据为准。
