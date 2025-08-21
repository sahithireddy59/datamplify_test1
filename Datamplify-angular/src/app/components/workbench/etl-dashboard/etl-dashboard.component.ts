import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';


interface Kpi {
  title: string;
  value: string;
  delta?: string;
  icon?: string;
  accent?: string;
}

@Component({
  selector: 'app-etl-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './etl-dashboard.component.html',
  styleUrl: './etl-dashboard.component.scss'
})
export class EtlDashboardComponent {
  kpis: Kpi[] = [
    { title: 'Total Flowboards', value: '24', delta: '+3 this week', icon: '🔁', accent: 'accent-blue' },
    { title: 'Total Task Plans', value: '18', delta: '+2 this week', icon: '🗂️', accent: 'accent-green' },
    { title: 'Success Rate', value: '94.2%', delta: '+1.2% today', icon: '✅', accent: 'accent-teal' },
    { title: 'Failure Rate', value: '5.8%', delta: '-0.3% today', icon: '❌', accent: 'accent-red' }
  ];

  activePipelines = [
    { title: 'Customer Data ETL', subtitle: 'Flowboard · Running for 2h 15m', color: 'blue' , status: 'Active'},
    { title: 'Sales Analytics Pipeline', subtitle: 'Task Plan · Running for 45m', color: 'green' , status: 'Active'},
    { title: 'Inventory Sync', subtitle: 'Flowboard · Running for 1h 22m', color: 'purple' , status: 'Active'},
  ];

  recentRuns = [
    { title: 'Product Catalog ETL', subtitle: 'Completed 15 minutes ago', status: 'Success' },
    { title: 'User Behavior Analysis', subtitle: 'Failed 32 minutes ago', status: 'Failed' },
    { title: 'Financial Reporting', subtitle: 'Completed 1 hour ago', status: 'Success' }
  ];

  statsFlowboard = [
    'Active Flowboards 8', 'Scheduled 12', 'Paused 3', 'Failed 1'
  ];

  statsTaskPlan = [
    'Active Task Plans 5', 'Scheduled 10', 'Paused 2', 'Failed 1'
  ];

  runStats = [
    'Total Runs Today 127', 'Successful Runs 119', 'Failed Runs 8', 'Avg Duration 23m'
  ];
}
