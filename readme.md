# 北师大校史 非官方整理

> 适逢北师大120周年校庆，我把之前参与的一个课题的成果简单整理了一下~
>
> 这是我用后端渲染的方式制作百科类网站的第一个尝试，在项目之初我几乎没有Web开发的知识，后来逐渐发现了后端模板框架的一些局限（当然我个人水平有限，没用到Jinja2的高级功能也是一大因素）。本来想做的很多功能最后都被搁置了，这个网站不出意外的话今后应该也不太会再更新了。我有在尝试写[一个支持更方便的组件化开发的模板引擎](https://github.com/CNSeniorious000/temponent)，也有在学习前端框架，但这个项目我想就此封存了。

### Deployed | 开始浏览

由于这个网站基本不更新，所以我写了个[SSG](https://www.gatsbyjs.com/docs/glossary/static-site-generator/)脚本，每次修改代码后将生成的静态资源上传到对象存储的服务（所以搜索功能暂且也不搞了）。关于SSG，以下是一个简短的定义：

> [Next.js docs:](https://nextjs.org/docs/basic-features/pages#static-generation)
> If a page uses **Static Generation**, the page HTML is generated at build time. That means in production, the page HTML is generated... This HTML will then be reused on each request. It can be cached by a CDN.

- 对象存储源站 > [bnu.muspimerol.site](//bnu.muspimerol.site/)
- 建议访问CDN站 > [bnu120.space](//bnu120.space/)

### Features | 特色

- SPA
  - 落地页为服务端渲染，导航到其它页面都是客户端差量渲染
  - 这降低了服务器渲染模板的压力、降低了带宽浪费、减少了页面闪烁、重复访问同一页面不用发起网络请求
  - 在鼠标悬浮时即触发预加载，减短导航时间
- PWA
  - 按教程写了非常简单的[`sw.js`](/static/sw.js)和[`manifest`](/static/manifest.json)
  - 现在可以将这个应用“添加到桌面”了
- SEO
  - 提供了各种 icon
    - `apple-touch-icon`[180x180](/static/icon/apple-touch-icon-180.png) [167x167](/static/icon/apple-touch-icon-167.png) [152x152](/static/icon/apple-touch-icon-152.png) [128x128](/static/icon/apple-touch-icon-128.png)
    - `favicon`[svg](/static/icon/favicon.svg) [png](/static/icon/favicon.png) [ico](/static/icon/favicon.ico)

### 开放平台 | API 文档

- Swagger UI > [CDN](https://bnu120.space/docs) / [源站](https://bnu.muspimerol.site/docs)
- ReDoc > [CDN](https://bnu120.space/redoc) / [源站](https://bnu.muspimerol.site/redoc)

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
