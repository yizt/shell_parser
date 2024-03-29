# shell_parser

   一个通用的命令行脚本管理工具,包括参数管理、shell脚本解析、通用脚本执行和日志记录;欢迎试用和反馈问题...
## 介绍
   本工程致力于实现命令行脚本的自动化;减少多段命令行执行流程中的人工干预;做到清晰的记录任何执行的脚本;
包括如下功能：
1. 统一的参数管理

    输入参数:数据时间,包括$datatime、$curday和$curmon三个参数
    
    自定义业务参数:其它个性化配置的输入参数;此类参数变化较大,每次执行可能不一样
    
    单值参数:命令中用到的比较固定的替换参数
    
    集合参数:对于一条配置的命令行会解析为多条待执行命令行
    
2. 通用的命令行脚本解析
    
3. 通用的命令行脚本执行

    日志记录(执行的命令、使用的参数、开始结束时间、执行耗时、输出信息、错误信息)
    从出错位置开始执行

## 依赖   
   本工程依赖关系型数据库,目前支持mysql或postgresql;依赖如下的python第三方包
```
SQLAlchemy
psycopg2
mysql-connector
```
   如下命令安装依赖
```shell
pip install -r requirements.txt
```

## 表结构说明

**参数配置表tb_param_cfg**

| 	字段名	            | 	中文名	    | 	备注	                                                                    |
|------------------|----------|-------------------------------------------------------------------------|
| 	param_type	     | 	参数类型	   | 	in-输入参数;single-单值参数;set-集合参数;cmdset-命令行参数;dependency-依赖参数;runtim运行时参数	 |
| 	param_name	     | 	参数名称	   | 		                                                                      |
| 	param_desc	     | 	参数说明	   | 		                                                                      |
| 	param_format	   | 	格式	     | 	不会实际起作用	                                                               |
| 	param_val_expr	 | 	参数值表达式	 | 	单值参数或集合参数的参数值表达式,执行该表达式获取参数值	                                          |
| 	enable	         | 	是否启用	   | 	1-启用;0-不启用	                                                            |
| 	replace_order	  | 	替换顺序	   | 	某些参数名称是其它参数的前缀情况下,替换有问题,指定顺序，保证替换正确	                                   |

**命令行配置表tb_cmd_cfg**

| 	字段名	      | 	中文名	   | 	备注	         |
|------------|---------|--------------|
| 	seq	      | 	序号	    | 	执行顺序	       |
| 	func_id	  | 	功能标识	  | 		           |
| 	cfg_key	  | 	命令行标志	 | 		           |
| 	memo	     | 	命令行备注	 | 		           |
| 	exec_cmd	 | 	命令行	   | 		           |
| 	enable	   | 	是否启用	  | 	1-启用;0-不启用	 |


**命令行运行表tb_execcmd**

| 	字段名	            | 	中文名	       | 	备注	         |
|------------------|-------------|--------------|
| 	datatime	       | 	数据时间	      | 		           |
| 	func_id	        | 	命令行标志	     | 		           |
| 	seq	            | 	序号	        | 		           |
| 	memo	           | 	命令行备注	     | 		           |
| 	exec_cmd	       | 	命令行	       | 		           |
| 	flag	           | 	命令返回标志	    | 	0-成功.其它-失败	 |
| 	err_msg	        | 	输出信息、错误信息	 | 		           |
| 	start_time	     | 	开始运行时间	    | 		           |
| 	end_time	       | 	结束运行时间	    | 		           |
| 	exec_elapsed	   | 	耗时(单位秒)	   | 		           |
| 	exec_date	      | 	运行日期	      | 		           |
| 	business_param	 | 	自定义业务参数	   | 		           |

## 创建表

在config.py中配置好数据库连接信息，执行如下命令即可
```shell
python db.py
```

## 使用例子

1. 参数配置
   
   tb_cmd_cfg表数据样例
   
| 	param_type	 | 	param_name	       | 	param_desc	                 | 	param_format	 | 	param_val_expr	                                                                                                                                                      | 	enable	 | 	replace_order	 |
|--------------|--------------------|------------------------------|----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|-----------------|
| 	in	         | 	$businessparam	   | 	业务参数	                       | 	(null)	       | 	(null)	                                                                                                                                                              | 	1	      | 	0	             |
| 	in	         | 	$curday	          | 	当日	                         | 	yyyymmdd	     | 	(null)	                                                                                                                                                              | 	1	      | 	0	             |
| 	in	         | 	$curmon	          | 	当月	                         | 	yyyymm	       | 	(null)	                                                                                                                                                              | 	1	      | 	0	             |
| 	set	        | 	$mons	            | 	测试月份	                       | 	(null)	       | 	select to_char(now() + (rownum &#124;&#124; ' mon')::interval,'YYYYMM') from (select row_number() over() as rownum from public.tb_param_cfg) as a where a.rownum<=2	 | 	1	      | 	1	             |
| 	set	        | 	$number	          | 	测试数字	                       | 	(null)	       | 	select rownum from (select row_number() over() as rownum from public.tb_param_cfg) as a where a.rownum<=2	                                                           | 	1	      | 	2	             |
| 	cmdset	     | 	$file_name	       | 	文件列表	                       | 	(null)	       | 	ls $odir	                                                                                                                                                            | 	1	      | 	1	             |
| 	dependency	 | 	$video_name	      | 	文件名不带路径	                    | 	(null)	       | 	(select reverse(split_part(reverse('$videos'),'/',1)))	                                                                                                              |
| 	runtime	    | 	$pno	             | 	进程编号	                       | 	(null)	       | 	(select mod($seq_no,$num_processes))	                                                                                                                                | 	1	      | 	1	             |
| 	single	     | 	$nextday	         | 	下一日	                        | 	yyyymmdd	     | 	to_char(to_date('$curday','YYYYMMDD') +  interval '1 day','YYYYMMDD')	                                                                                               | 	1	      | 	1	             |
| 	single	     | 	$template_dir	    | 	模板文件目录	                     | 	(null)	       | 	'/sdb/tmp/users/yizt/config.template'	                                                                                                                               | 	1	      | 	2	             |
| 	single	     | 	$data_dir	        | 	当前训练数据目录	                   | 	(null)	       | 	'/sdb/tmp/users/yizt/data/$datatime.$num_images.$num_steps.$gpu_id'	                                                                                                 | 	1	      | 	3	             |
| 	single	     | 	$tf_research_dir	 | 	tensorflow model reseach目录	 | 	(null)	       | 	'/sdb/tmp/users/yizt/models/research'	                                                                                                                               | 	1	      | 	5	             |
| 	single	     | 	$syn_dir	         | 	图像合成工程目录	                   | 	(null)	       | 	'/sdb/tmp/users/yizt/Yolo_as_Template_Matching'	                                                                                                                     | 	1	      | 	4	             |

2. 脚本配置
    一个配置脚本例子(tb_cmd_cfg表exec_cmd字段);
```
python /sdb/tmp/users/yizt/window_analyze_multi_file.py \
$data_dir/image_generated/classes.names \
$data_dir/inferences \
$data_dir/window.multi_file.$datatime.$num_images.$num_steps.$gpu_id.csv
```
3. 命令执行
```shell
python main.py inference_yizt 20191005 normal num_images=50000,num_steps=150000,gpu_id=5
```
4. 日志查看
```sql
select * from tb_execcmd
  where func_id='inference_yizt' and datatime='20191005' and business_param='num_images=50000,num_steps=150000,gpu_id=5'  
 order by  seq;
```

## 更新记录

1、20221214日，增加命令行集合参数，`param_type`为`cmdset`; 如下例：

|	param_type	|	param_name	|	param_desc	|	param_format	|	param_val_expr	|	enable	|	replace_order	|
|	----	|	----	|	----	|	----	|	----	|	----	|	----	|
|	cmdset	|	$video_list	|	测试视频列表	|	(null)	|	ls $vdir	|	1	|	0	|

`$video_list` 会被替换为多条执行命令，每个值为`ls $vdir`执行的结果中的元素，`$vdir`是`single`类型参数或者业务参数

## 参数用法举例

### cmdset
通过shell命令行执行的替换参数
```shell
for fn in $(find $odir -maxdepth 1 -mmin +1 -type d -printf '%f\n' | sort | head -n $topn)
do
if [ ! -f "$vdir/$fn.mp4"  ];then
echo $fn
fi
done 
```

```shell
for fp in $(ssh -p 57800 user_name@ip "find /path/to/dir -size +100M -ctime -1 | sort")
do
fn=`echo $fp| awk -F '/' '{print $5}'`
#echo $fn
if [ ! -f "$vdir/$fn" ];then
echo $fp
fi
done
```

```shell
for fn in $(find $vdir -maxdepth 1 -mmin +10 -ctime -8 -type d -printf '%f\n' | sort | head -n $topn)
do
vprefix=`echo $fn| awk -F '.' '{print $1}'`
if [ ! -d "$odir/$vprefix" ];then
echo $fn
fi
done 
```

### dependency
依赖参数,依赖于某一个(刚好一个)集合参数:

`(select reverse(split_part(reverse('$mask_test_dir_paths'),'/',1)))`

### runtime
`$seq_no`: 代表生成的`tb_execcmd`表中`seq`字段的值</br>
`$num_processes`: 代表多线程执行时,线程数</br>
显然都是生成运行脚步后,或者执行的时候才清楚具体的值,依赖于这两个参数的参数都是运行时参数,如下例子:</br>
`$pno`: 哪个进程执行此seq `(select mod($seq_no,$num_processes))`</br>
`$port_no`: 端口号 `(select 8000+mod($seq_no,2))`</br>


## toList
1、数据库表默认值导入
2、