import { Component, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
// import { NgbButtonsModule } from '@ng-bootstrap/ng-bootstrap';
import { NgApexchartsModule, ApexAxisChartSeries, ApexChart, ApexXAxis, ApexYAxis, ApexStroke, ApexDataLabels, ApexGrid, ApexTooltip, ApexLegend, ApexPlotOptions, ApexResponsive, ApexNonAxisChartSeries, ApexFill, ApexMarkers, ApexTitleSubtitle } from 'ng-apexcharts';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { pie } from 'd3';

export type MixedChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  yaxis: ApexYAxis | ApexYAxis[];
  stroke: ApexStroke;
  dataLabels: ApexDataLabels;
  grid: ApexGrid;
  tooltip: ApexTooltip;
  legend: ApexLegend;
  plotOptions?: ApexPlotOptions;
  markers?: ApexMarkers;
  fill?: ApexFill;
};

export type PieChartOptions = {
  series: ApexNonAxisChartSeries;
  chart: ApexChart;
  labels: string[];
  legend: ApexLegend;
  tooltip: ApexTooltip;
  responsive: ApexResponsive[];
  fill?: ApexFill;
  stroke?: ApexStroke;
};

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, NgApexchartsModule, FormsModule, ReactiveFormsModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent {
  kpiData = [
    { title: 'Success Rate', value: '98.5%', change: '+2.1%', trend: 'up', icon: 'bi-bullseye', color: 'emerald', description: 'Percentage of successful executions across all flows' },
    { title: 'Failure Rate', value: '2.5%', change: '-1.2%', trend: 'down', icon: 'bi-activity', color: 'blue', description: 'Percentage of executions that ended in failure' },
    { title: 'Total FLowboards', value: '156', change: '+8', trend: 'up', icon: 'bi-database', color: 'violet', description: "Number of active flowboards monitored in the system" },
    { title: 'Total Taskplans', value: '89', change: '+3', trend: 'up', icon: 'bi-lightning-charge', color: 'amber', description: 'Number of active Taskplans monitored in the system' },
  ];

  topRunsData = [
    { name: 'Customer Sync', flowBoard: 145, taskPlan: 98, flowBoardRuns: 45, taskPlanRuns: 35 },
    { name: 'Sales Report', flowBoard: 128, taskPlan: 87, flowBoardRuns: 42, taskPlanRuns: 32 },
    { name: 'Inventory Update', flowBoard: 98, taskPlan: 76, flowBoardRuns: 38, taskPlanRuns: 28 },
    { name: 'User Analytics', flowBoard: 76, taskPlan: 65, flowBoardRuns: 28, taskPlanRuns: 25 },
    { name: 'Log Processing', flowBoard: 54, taskPlan: 48, flowBoardRuns: 22, taskPlanRuns: 20 },
  ];

  flowBoardData = [
    { name: 'Success', value: 78, color: '#10b981' },
    { name: 'Failed', value: 15, color: '#ef4444' },
    { name: 'Running', value: 7, color: '#f59e0b' },
  ];

  taskPlanData = [
    { name: 'Success', value: 82, color: '#10b981' },
    { name: 'Failed', value: 12, color: '#ef4444' },
    { name: 'Running', value: 6, color: '#f59e0b' },
  ];

  recentItems = [
    { id: 1, name: 'Customer Data Sync', type: 'FlowBoard', status: 'success', time: '2 mins ago', records: '12.4K' },
    { id: 2, name: 'Daily Report Generation', type: 'TaskPlan', status: 'running', time: '5 mins ago', records: '8.9K' },
    { id: 3, name: 'Inventory Update', type: 'FlowBoard', status: 'failed', time: '8 mins ago', records: '2.1K' },
    { id: 4, name: 'User Analytics Processing', type: 'TaskPlan', status: 'success', time: '12 mins ago', records: '5.2K' },
    { id: 5, name: 'Log Aggregation', type: 'FlowBoard', status: 'running', time: '15 mins ago', records: '18.7K' },
    { id: 6, name: 'Email Campaign Sync', type: 'TaskPlan', status: 'success', time: '18 mins ago', records: '3.4K' },
    { id: 7, name: 'Database Backup', type: 'FlowBoard', status: 'failed', time: '22 mins ago', records: '45.2K' },
    { id: 8, name: 'API Monitoring', type: 'TaskPlan', status: 'success', time: '25 mins ago', records: '1.8K' },
  ];

  // ===== UI state =====
  chartMode : string = 'flowboard'; // 'flowBoard' or 'taskPlan'

  currentPie : any[] = [];

  // ===== Charts (ApexCharts) =====
  mixedOptions: any = {};
  pieOptions: any = {};

  constructor() {
  }

  activeTab: 'success' | 'failure' | 'running' | 'recent' = 'success';

  flowData: any[] = [
    { title: 'Customer Pipeline - Processing Complete', runs: 142, timeAgo: '2 mins ago', type: 'success' },
    { title: 'Analytics Flow - Data Validated', runs: 121, timeAgo: '5 mins ago', type: 'success' },
    { title: 'Sales Data Processing - Transformation Done', runs: 89, timeAgo: '8 mins ago', type: 'success' },
    { title: 'Data Validation - Quality Check Passed', runs: 76, timeAgo: '12 mins ago', type: 'success' },
    { title: 'Customer Pipeline - Failed at Step 3', runs: 15, timeAgo: '4 mins ago', type: 'failure' },
    { title: 'Data Ingestion - Running...', runs: 32, timeAgo: 'Just now', type: 'running' },
    { title: 'Analytics Flow - Recently Triggered', runs: 50, timeAgo: '1 min ago', type: 'recent' },
  ];

  // Return filtered list based on active tab
  get filteredData() {
    return this.flowData.filter(f => f.type === this.activeTab);
  }

  setTab(tab: 'success' | 'failure' | 'running' | 'recent') {
    this.activeTab = tab;
  }

  changeChartMode(){
    this.currentPie = this.chartMode === 'flowboard' ? this.flowBoardData : this.taskPlanData;
    if(this.pieOptions?.series){
      this.pieOptions.series = this.currentPie.map(p => p.value);
      this.pieOptions.labels = this.currentPie.map(p => p.name);
      this.pieOptions.colors = ['#10b981', '#ef4444', '#f59e0b'];
    }
  }

  ngOnInit() {
    this.changeChartMode();
    
    this.pieOptions = {
      series: this.currentPie.map(p => p.value),
      chart: { type: 'donut', height: 300 },
      labels: this.currentPie.map(p => p.name),
      legend: { position: 'bottom' },
      tooltip: { theme: 'light' },
      responsive: [{ breakpoint: 992, options: { chart: { height: 280 } } }],
      colors: ['#10b981', '#ef4444', '#f59e0b'],
      stroke: { width: 2 }
    };

    this.mixedOptions = {
      series: [
        { name: 'FlowBoard Records', type: 'column', data: this.topRunsData.map(d => d.flowBoard) },
        { name: 'TaskPlan Records', type: 'column', data: this.topRunsData.map(d => d.taskPlan) },
        { name: 'FlowBoard Runs', type: 'line', data: this.topRunsData.map(d => d.flowBoardRuns) },
        { name: 'TaskPlan Runs', type: 'line', data: this.topRunsData.map(d => d.taskPlanRuns) },
      ],
      chart: { type: 'line', height: 360, toolbar: { show: false }, foreColor: '#64748b' },
      xaxis: { categories: this.topRunsData.map(d => d.name), axisBorder: { show: true }, axisTicks: { show: true } },
      yaxis: [
        { title: { text: 'Records' } },
        { opposite: true, title: { text: 'Runs' } },
      ],
      stroke: { width: [0, 0, 3, 3], curve: 'smooth' },
      dataLabels: { enabled: false },
      grid: { borderColor: 'rgba(14,165,233,.15)' },
      tooltip: { theme: 'light' },
      legend: { position: 'bottom' },
      fill: {
        type: ['gradient', 'gradient', 'solid', 'solid'],
        gradient: {
          shadeIntensity: .7,
          opacityFrom: .8,
          opacityTo: .3,
          stops: [0, 100]
        }
      },
      plotOptions: {
        bar: { columnWidth: '40%', borderRadius: 6 }
      },
      markers: { size: [0, 0, 5, 5] },
    };
  }
}
