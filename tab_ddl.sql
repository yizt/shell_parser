===============================mysql表结构==========================


CREATE TABLE `tb_cmd_cfg` (
  `seq` float NOT NULL,
  `func_id` varchar(40) NOT NULL,
  `cfg_key` varchar(40) DEFAULT NULL,
  `memo` varchar(100) DEFAULT NULL,
  `exec_cmd` longtext,
  `enable` varchar(1) DEFAULT NULL,
  PRIMARY KEY (`seq`,`func_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_param_cfg` (
  `param_type` varchar(20) NOT NULL DEFAULT '',
  `param_name` varchar(40) NOT NULL DEFAULT '',
  `param_desc` varchar(200) DEFAULT NULL,
  `param_format` varchar(40) DEFAULT NULL,
  `param_val_expr` text,
  `enable` varchar(1) DEFAULT NULL,
  `replace_order` bigint(22) DEFAULT NULL,
  PRIMARY KEY (`param_type`,`param_name`),
  UNIQUE KEY `IDX_TB_PARAM_CFG` (`param_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_execcmd` (
  `datatime` varchar(8) NOT NULL DEFAULT '',
  `func_id` varchar(40) NOT NULL DEFAULT '',
  `seq` bigint(22) NOT NULL DEFAULT '0',
  `memo` varchar(100) DEFAULT NULL,
  `exec_cmd` longtext,
  `flag` smallint(22) DEFAULT NULL,
  `err_msg` text,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `exec_elapsed` bigint(22) DEFAULT NULL,
  `exec_date` date DEFAULT NULL,
  `business_param` varchar(40) NOT NULL DEFAULT '',
  PRIMARY KEY (`datatime`,`func_id`,`seq`,`business_param`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;