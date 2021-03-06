# 无线技术比较

**注意**： 5分最好， 1分最差

| 项目 | 433 | BLE Mesh | zigbee | thread | wifi |
| ---- | --- | -------- | ------ | ------ | ---- |
| 类型 | 点到点 | PAN | PAN | PAN | LAN |
| 频段 | 433Mhz | 2.4G | 2.4G | 2.4G | 2.4/5G|
| 双向 | 不支持 | 支持 | 支持 | 支持 | 支持 |
| 性能* | x     | 1    | 2    | 3    | 取决于AP |
| 低功耗 | 自主支持 | 支持 | 支持 | 支持 | 不支持 |
| 成熟度 | 成熟 | 中等 | 成熟 | 中等 | 成熟 |
| 生态   | x    | 少   | 多   | 国内少 | 多 |
| 应用层模型 | 无 | 有   | ZDO   | 有   | 无 |
| 模块复杂度** | 低 | 中 | 高 | 高 | 低 |
| 现成模块   | 有 | 有 | 有 | x | 有 |
| 应用复杂度*** | 高 | 中 | 中 | 高 | 低 |
| 网关 | 必须 | 必须 | 必须 | 必须 | 不需要 |
| 模块成本   | 5  | 4 | 3 | 3 | 1 |
| 市场热度**** | x | 高 | 高 | 无 | 高 |
| 技术可重用性 | 无 | 可 | 可 | 可 | 可 |

\* 性能本质取决于分包和路由，参阅 [AN1142: Mesh Network Performance
Comparison](https://www.silabs.com/documents/public/application-notes/an1142-mesh-network-performance-comparison.pdf)

** 自己开发带模型的软件复杂度， 如果直接控制IO的话，都差不都

*** 主控或支持软件复杂度

**** 市场热度是看其他公司网站上的产品是否有此品类
