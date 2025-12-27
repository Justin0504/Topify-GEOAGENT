"""
required_open_webui_version: 0.6.0
description: Project Management Tool for task tracking and client collaboration
requirements: python-docx
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

try:
    from docx import Document
    from docx.shared import Inches
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class Tools:
    class Valves(BaseModel):
        default_weeks: int = Field(
            default=12,
            description="Default project duration in weeks"
        )

    def __init__(self):
        self.valves = self.Valves()

    async def create_gantt_chart(
        self,
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate Gantt chart data for project tasks
        
        :param tasks: List of tasks with name, start_date, end_date, assignee (optional)
        :return: Gantt chart data
        """
        try:
            # Process tasks
            processed_tasks = []
            for i, task in enumerate(tasks):
                start_date = self._parse_date(task.get("start_date"))
                end_date = self._parse_date(task.get("end_date"))
                
                if start_date and end_date:
                    duration = (end_date - start_date).days
                    processed_tasks.append({
                        "task_id": i + 1,
                        "name": task.get("name", f"Task {i+1}"),
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                        "duration_days": duration,
                        "assignee": task.get("assignee", "未分配"),
                        "status": task.get("status", "待开始"),
                        "progress": task.get("progress", 0)
                    })
            
            # Calculate project timeline
            if processed_tasks:
                start_dates = [datetime.strptime(t["start_date"], "%Y-%m-%d") for t in processed_tasks]
                end_dates = [datetime.strptime(t["end_date"], "%Y-%m-%d") for t in processed_tasks]
                project_start = min(start_dates)
                project_end = max(end_dates)
                project_duration = (project_end - project_start).days
            else:
                project_start = datetime.now()
                project_end = project_start + timedelta(days=30)
                project_duration = 30
            
            return {
                "success": True,
                "tasks": processed_tasks,
                "project_timeline": {
                    "start_date": project_start.strftime("%Y-%m-%d"),
                    "end_date": project_end.strftime("%Y-%m-%d"),
                    "duration_days": project_duration
                },
                "summary": {
                    "total_tasks": len(processed_tasks),
                    "completed_tasks": len([t for t in processed_tasks if t["status"] == "已完成"]),
                    "in_progress": len([t for t in processed_tasks if t["status"] == "进行中"]),
                    "pending": len([t for t in processed_tasks if t["status"] == "待开始"])
                },
                "gantt_data": self._format_gantt_data(processed_tasks)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating Gantt chart: {str(e)}"
            }

    async def generate_weekly_report(
        self,
        project_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate automated weekly report
        
        :param project_info: Project information including tasks, progress, milestones
        :return: Weekly report content
        """
        try:
            current_week = datetime.now().strftime("%Y年第%W周")
            week_start = datetime.now() - timedelta(days=datetime.now().weekday())
            week_end = week_start + timedelta(days=6)
            
            tasks = project_info.get("tasks", [])
            completed_this_week = [t for t in tasks if t.get("completed_date") and 
                                   week_start <= datetime.strptime(t["completed_date"], "%Y-%m-%d") <= week_end]
            in_progress = [t for t in tasks if t.get("status") == "进行中"]
            upcoming = [t for t in tasks if t.get("status") == "待开始"][:5]
            
            report = {
                "success": True,
                "week": current_week,
                "week_range": f"{week_start.strftime('%Y-%m-%d')} 至 {week_end.strftime('%Y-%m-%d')}",
                "summary": {
                    "completed_tasks": len(completed_this_week),
                    "in_progress_tasks": len(in_progress),
                    "upcoming_tasks": len(upcoming)
                },
                "completed_this_week": [
                    {
                        "task": t.get("name", ""),
                        "completed_date": t.get("completed_date", ""),
                        "assignee": t.get("assignee", "")
                    }
                    for t in completed_this_week
                ],
                "in_progress": [
                    {
                        "task": t.get("name", ""),
                        "progress": t.get("progress", 0),
                        "assignee": t.get("assignee", "")
                    }
                    for t in in_progress
                ],
                "upcoming": [
                    {
                        "task": t.get("name", ""),
                        "start_date": t.get("start_date", ""),
                        "assignee": t.get("assignee", "")
                    }
                    for t in upcoming
                ],
                "next_week_plan": self._generate_next_week_plan(tasks, week_end),
                "recommendations": self._generate_recommendations(tasks)
            }
            
            return report
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating weekly report: {str(e)}"
            }

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str:
            return None
        
        try:
            # Try different date formats
            formats = ["%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y"]
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
            return None
        except:
            return None

    def _format_gantt_data(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format tasks for Gantt chart display"""
        return [
            {
                "task": t["name"],
                "start": t["start_date"],
                "end": t["end_date"],
                "duration": t["duration_days"],
                "assignee": t["assignee"],
                "status": t["status"]
            }
            for t in tasks
        ]

    def _generate_next_week_plan(self, tasks: List[Dict[str, Any]], week_end: datetime) -> List[str]:
        """Generate next week plan"""
        next_week_start = week_end + timedelta(days=1)
        next_week_end = next_week_start + timedelta(days=6)
        
        upcoming_tasks = [
            t for t in tasks
            if t.get("start_date") and
            next_week_start <= datetime.strptime(t["start_date"], "%Y-%m-%d") <= next_week_end
        ]
        
        return [t.get("name", "") for t in upcoming_tasks[:5]]

    def _generate_recommendations(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on tasks"""
        recommendations = []
        
        overdue = [t for t in tasks 
                   if t.get("end_date") and 
                   datetime.strptime(t["end_date"], "%Y-%m-%d") < datetime.now() and
                   t.get("status") != "已完成"]
        
        if overdue:
            recommendations.append(f"有 {len(overdue)} 个任务已逾期，建议优先处理")
        
        high_priority = [t for t in tasks if t.get("priority") == "高" and t.get("status") != "已完成"]
        if high_priority:
            recommendations.append(f"有 {len(high_priority)} 个高优先级任务待完成")
        
        return recommendations

