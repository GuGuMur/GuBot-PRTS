## GuBot-PRTS
本仓库为GuBot装置小队功能的分支，不包括所有QQGuBot功能。

## [插件](/src/plugins)
* [reply_event_processor](/src/plugins/reply_event_processor/)：回复类信息的预处理，GuBot处理明日方舟游戏内公告的基础
* [akdata_update](/src/plugins/akdata_update/)：用来手动更新[ArknightsGameData库](https://github.com/Kengxxiao/ArknightsGameData)（虽然设置了5分钟自动`git pull` 但这个北京的腾讯云服务器怎么连GitHub高低带点抽风
* [prts_rc](/src/plugins/prts_rc/)：每两分钟向装置小队群里自动转发最新最热Topic和Talk页编辑记录
* [prts_announce](/src/plugins/prts_announce/)：每一分钟向装置小队群里转发yj最新最热游戏内公告
    * [deal_announce](/src/plugins/prts_announce/plugins/deal_announce/)：处理游戏公告为适合活动页面的格式
    * [old_gacha](/src/plugins/prts_announce/plugins/old_gacha/)：处理中坚寻访
    * [special_gacha](/src/plugins/prts_announce/plugins/special_gacha)：处理限时寻访
    * [weekly_gacha](/src/plugins/prts_announce/plugins/weekly_gacha)：处理周常寻访
* [prts_stage](/src/plugins/prts_stage/)：处理[新增关卡页面](https://prts.wiki/id/18670)的关卡的特殊地块与装置，并将这些页面的地块内容整合到[User:GuBot/newtiles](https://prts.wiki/w/User:GuBot/newtiles)中

