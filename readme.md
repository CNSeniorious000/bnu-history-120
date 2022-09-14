# 北师大校史 非官方整理

> 适逢北师大120周年校庆，我把之前参与的一个课题的成果简单整理了一下~

### Deployed | 开始浏览

- 较慢更新的CDN站 > [bnu120.space](https://bnu120.space/北师大)
- 较快更新的CDN站 > [bnu.muspimerol.site](https://bnu.muspimerol.site/北师大)
- 源站（即时更新）> [https://muspimerol.site:12000](https://muspimerol.site:12000/北师大)

### Features | 特色

- 适配深色模式
  - `<link rel="stylesheet" href="..." media="(prefers-color-scheme: light)">`是一种方式，但在Safari中，打开页面后切换深浅色模式则不会重载css
  - `@media (prefers-color-scheme: light) { ... }`是另一种方式，但会增大一丁点加载的css的体积
- 适配移动端
  - `<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">`
  - 页脚导航栏，竖屏下`flex-direction: column;`，横屏下`flex-direction: row;`
  - 内边距`padding: calc(min(10%, 7em));`
  - 总体套在一个弹性盒中
    - 设定`min-height: 100vh;`保证底色不漏
    - 设定`justify-content: space-between;`保证正文居上，页脚居下
- 悬浮秒开 (类似各前端框架的`prefetch`) 同时兼顾 SEO (整页服务端渲染)
  1. 既然要SEO，必须保证直接访问每个页面都是服务端渲染好的
  2. 但是大部分页面页眉页脚、样式表和脚本 都是相同的，因此提供了**只返回正文和元数据的接口**，用于服务端渲染 [Swagger文档](/docs#/API) [ReDoc文档](/redoc#tag/API)
  3. 服务端预加载、差量更新步骤  //TODO: 添加时序图
     1. **鼠标悬浮**，触发预加载
     2. **鼠标点击**，触发dom更新（用`innerHTML`直接修改）、url更新（通过`history.pushState`压栈）
     3. 监听`window.onpopstate`事件，触发dom更新
     4. 预加载缓存（用一个简单的`Map`实现）跨页面共享，因此也比`<link rel="prefetch">`省流
  4. 对所有数据请求检查etag, 尽量返回304状态码
- 提供了各种 icon
  - `apple-touch-icon`[180x180](/icon/apple-touch-icon-180.png) [167x167](/icon/apple-touch-icon-167.png) [152x152](/icon/apple-touch-icon-152.png) [128x128](/icon/apple-touch-icon-128.png)
  - `favicon`[svg](/icon/favicon.svg) [png](/icon/favicon.png) [ico](/icon/favicon.ico)

### 开放平台 | API 文档

- Swagger UI > [CDN-1](https://bnu120.space/docs) / [CDN-2](https://bnu.muspimerol.site/docs) / [源站](https://muspimerol.site:12000/docs)
- ReDoc > [CDN-1](https://bnu120.space/redoc) / [CDN-2](https://bnu.muspimerol.site/redoc) / [源站](https://muspimerol.site:12000/redoc)

### to-do

- 适配 Open Graph 特性
- 学校视图：左边目录（参考mdn右边），右边正文
- 人物试图：左边头像
- 列表视图：多列布局，头像+姓名
- 预算阅读时间
- 扫描全文，标注所有站内链接
- 首页展示

### Repositories | 项目相关链接

- <https://github.com/CNSeniorious000/bnu-history-120>
- <https://jihulab.com/CNSeniorious000/bnu-history-120>
- <https://jihulab.com/CNSeniorious000/bnu-history-parser>
- <https://jihulab.com/CNSeniorious000/bnu-history-parser-2>
