# -*- coding: utf-8 -*-
"""
 @File    : parse_log_info.py
 @Time    : 2023/10/9 1:59 PM
 @Author  : yizuotian
 @Description    :
"""
import argparse
import db
from config import cur_config as cfg


class ParserFunction(object):
    @staticmethod
    def eval_llm(cmd_info):
        """

        :param cmd_info:
        :return:
        """
        time_cost = cmd_info.exec_elapsed
        memo = cmd_info.memo
        lines = cmd_info.err_msg.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("dataset ") and "version" in line:
                print(memo.split("=")[1], time_cost)
                j = i
                while "OpenCompass" not in lines[j]:
                    print(lines[j])
                    j += 1
                return

    @staticmethod
    def gyy_ft_eval(cmd_info):
        """

        :param cmd_info:
        :return:
        """
        time_cost = cmd_info.exec_elapsed
        memo = cmd_info.memo
        lines = cmd_info.err_msg.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("dataset ") and "version" in line:
                _, model_name, ft_type = memo.split(";")
                print(model_name.split("=")[1], ft_type.split("=")[1], time_cost)
                j = i
                while "OpenCompass" not in lines[j]:
                    print(lines[j])
                    j += 1
                return

    def gyy_eval(self, cmd_info):
        return self.gyy_ft_eval(cmd_info)

    def efficient_tuning(self, cmd_info):
        return self.gyy_ft_eval(cmd_info)

    def eval_efficient_tuning(self, cmd_info):
        return self.gyy_ft_eval(cmd_info)

    @staticmethod
    def dummy_func(**kwargs):
        print("here")
        print(kwargs)


def main(args):
    session = db.get_session(cfg.url)
    cmd_info_list: list[db.TbExecCmd] = db.get_exec_cmd(session, args.datatime, args.func_id, args.business_param)
    o = ParserFunction()
    func = getattr(o, args.func_id)
    print(len(cmd_info_list))
    for cmd_info in cmd_info_list:
        func(cmd_info)


if __name__ == '__main__':
    """
    Useage:
    python parse_log_info.py --datatime 20231001 --func_id eval_llm --business_param gpu_id=2,dataset=fault_pump_gen

    python parse_log_info.py --datatime 20231007 --func_id eval_llm --business_param gpu_id=1,dataset=zkyg_choice_gen_3ad45s*zkyg_tof_gen_794a5c
    
    python parse_log_info.py --datatime 20231007 --func_id gyy_ft_eval --business_param epochs=3,bs=16,max_samples=500000,gpu_id=0
    
    python parse_log_info.py --datatime 20231012 --func_id gyy_eval --business_param epochs=3,bs=16,max_samples=500000
        
    python parse_log_info.py --datatime 20231013 --func_id gyy_eval --business_param epochs=3,bs=24,max_samples=500000,gpu_id=0

    """
    paser = argparse.ArgumentParser()
    paser.add_argument('--datatime', type=str, default='20231007', help='')
    paser.add_argument('--func_id', type=str, default='eval_llm', help='')
    paser.add_argument('--business_param', type=str,
                       default='gpu_id=1,dataset=zkyg_choice_gen_3ad45s*zkyg_tof_gen_794a5c', help='')
    # cmd_line = 'python parse_log_info.py --datatime 20231007 --func_id eval_llm --business_param gpu_id=1,dataset=zkyg_choice_gen_3ad45s*zkyg_tof_gen_794a5c'
    arguments = paser.parse_args()
    print(arguments)
    main(arguments)
