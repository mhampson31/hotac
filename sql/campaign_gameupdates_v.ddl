-- django.campaign_gameupgrades_v source

CREATE OR REPLACE
ALGORITHM = UNDEFINED VIEW `campaign_gameupgrades_v` AS
select
    concat(`p`.`id`, 'P') AS `id`,
    `p`.`id` AS `base_id`,
    'P' AS `base`,
    concat(`p`.`name`, ' - ', `c`.`name`) AS `name`,
    `p`.`initiative` AS `cost`,
    `p`.`description` AS `description`,
    `p`.`ai_description` AS `ai_description`,
    `p`.`type` AS `type`,
    `p`.`type2` AS `type2`,
    `p`.`charges` AS `charges`,
    `p`.`force` AS `force`
from
    (`xwtools_pilot` `p`
join `xwtools_chassis` `c` on
    (`c`.`id` = `p`.`chassis_id`))
union
select
    concat(`u`.`id`, 'U') AS `id`,
    `u`.`id` AS `base_id`,
    'U' AS `base`,
    `u`.`name` AS `name`,
    `u`.`cost` AS `cost`,
    `u`.`description` AS `description`,
    `u`.`ai_description` AS `ai_description`,
    `u`.`type` AS `type`,
    `u`.`type2` AS `type2`,
    `u`.`charges` AS `charges`,
    `u`.`force` AS `force`
from
    `xwtools_upgrade` `u`;
