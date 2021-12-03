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
  `business_param` varchar(200) NOT NULL DEFAULT '',
  PRIMARY KEY (`datatime`,`func_id`,`seq`,`business_param`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



===================postgresql表结构=============

CREATE TABLE public.tb_cmd_cfg (
	seq float8 NOT NULL,
	func_id varchar(40) NOT NULL,
	cfg_key varchar(40) NULL,
	memo varchar(100) NULL,
	exec_cmd text NULL,
	"enable" varchar(1) NULL,
	CONSTRAINT tb_cmd_cfg_pkey PRIMARY KEY (seq, func_id)
);


CREATE TABLE public.tb_param_cfg (
	param_type varchar(20) NOT NULL,
	param_name varchar(40) NOT NULL,
	param_desc varchar(200) NULL,
	param_format varchar(40) NULL,
	param_val_expr text NULL,
	"enable" varchar(1) NULL,
	replace_order int8 NULL,
	CONSTRAINT tb_param_cfg_pkey PRIMARY KEY (param_type, param_name),
	CONSTRAINT tb_param_cfg_un UNIQUE (param_name)
);

CREATE TABLE public.tb_execcmd (
	datatime varchar(8) NOT NULL,
	func_id varchar(40) NOT NULL,
	seq int8 NOT NULL,
	memo varchar(100) NULL,
	exec_cmd text NULL,
	flag int2 NULL,
	err_msg text NULL,
	start_time timestamp NULL,
	end_time timestamp NULL,
	exec_elapsed int8 NULL,
	exec_date date NULL,
	business_param varchar(200) NOT NULL,
	CONSTRAINT tb_execcmd_pkey PRIMARY KEY (datatime, seq, func_id, business_param)
);


======样例数据======
INSERT INTO public.tb_param_cfg (param_type,param_name,param_desc,param_format,param_val_expr,"enable",replace_order) VALUES
('in','$businessparam','业务参数',NULL,NULL,'1',0)
,('in','$curday','当日','yyyymmdd',NULL,'1',0)
,('in','$curmon','当月','yyyymm',NULL,'1',0)
,('single','$nextday','下一日','yyyymmdd','to_char(to_date(''$curday'',''YYYYMMDD'') +  interval ''1 day'',''YYYYMMDD'')','1',1)
,('set','$mons','测试月份',NULL,'select to_char(now() + (rownum || '' mon'')::interval,''YYYYMM'') from (select row_number() over() as rownum from public.tb_param_cfg) as a where a.rownum<=2','1',1)
,('set','$number','测试数字',NULL,'select rownum from (select row_number() over() as rownum from public.tb_param_cfg) as a where a.rownum<=2','1',2)
;


INSERT INTO public.tb_cmd_cfg (seq,func_id,cfg_key,memo,exec_cmd,"enable") VALUES
(2,'test_param',NULL,'测试single参数','$nextday','1')
,(3.5,'test_param',NULL,'测试set参数','$mons,$number','1')
,(1,'test_param',NULL,'测试in参数','$curday,$curmon,$a,$b','1')
;