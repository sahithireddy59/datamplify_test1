import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { WorkbenchService } from '../../workbench/workbench.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrl: './admin-dashboard.component.scss'
})
export class AdminDashboardComponent implements OnInit {
  
  statistics = {
    totalUsers: 0,
    activeUsers: 0,
    totalRoles: 0,
    totalFlowBoards: 0,
    totalConnections: 0,
    runningFlows: 0
  };

  recentActivities: any[] = [];
  systemHealth = {
    status: 'healthy',
    uptime: '99.9%',
    lastBackup: new Date(),
    diskUsage: '45%'
  };

  quickActions = [
    {
      title: 'Add New User',
      icon: 'fa fa-user-plus',
      route: '/admin/users',
      color: 'primary'
    },
    {
      title: 'Create Role',
      icon: 'fa fa-shield-alt',
      route: '/admin/roles',
      color: 'success'
    },
    {
      title: 'System Settings',
      icon: 'fa fa-cog',
      route: '/admin/settings',
      color: 'info'
    },
    {
      title: 'View Logs',
      icon: 'fa fa-file-alt',
      route: '/admin/logs',
      color: 'warning'
    }
  ];

  constructor(private workbenchService: WorkbenchService) {}

  ngOnInit() {
    this.loadStatistics();
    this.loadRecentActivities();
  }

  loadStatistics() {
    // Load user statistics
    const userPayload = { page_number: 1, page_size: 1000, search: '' };
    this.workbenchService.getUserList(userPayload).subscribe({
      next: (data: any) => {
        this.statistics.totalUsers = data.total_records || 0;
        this.statistics.activeUsers = data.data?.filter((u: any) => u.is_active).length || 0;
      },
      error: (err) => console.error('Error loading users:', err)
    });

    // Load role statistics
    const rolePayload = { page_number: 1, page_size: 1000, search: '' };
    this.workbenchService.getSavedRolesList(rolePayload).subscribe({
      next: (data: any) => {
        this.statistics.totalRoles = data.total_records || 0;
      },
      error: (err) => console.error('Error loading roles:', err)
    });

    // Load FlowBoard statistics - using mock data for now
    // TODO: Add getFlowboardList method to WorkbenchService
    this.statistics.totalFlowBoards = 0;

    // Load connection statistics - using mock data for now
    // TODO: Add getConnectionsList method to WorkbenchService
    this.statistics.totalConnections = 0;
  }

  loadRecentActivities() {
    // Mock recent activities - replace with actual API call
    this.recentActivities = [
      {
        user: 'Admin User',
        action: 'Created new FlowBoard',
        target: 'Customer ETL Flow',
        timestamp: new Date(Date.now() - 1000 * 60 * 5),
        icon: 'fa fa-plus-circle',
        color: 'success'
      },
      {
        user: 'John Doe',
        action: 'Updated role permissions',
        target: 'Data Analyst Role',
        timestamp: new Date(Date.now() - 1000 * 60 * 15),
        icon: 'fa fa-edit',
        color: 'info'
      },
      {
        user: 'Admin User',
        action: 'Added new user',
        target: 'jane.smith@example.com',
        timestamp: new Date(Date.now() - 1000 * 60 * 30),
        icon: 'fa fa-user-plus',
        color: 'primary'
      },
      {
        user: 'System',
        action: 'Completed backup',
        target: 'Database Backup',
        timestamp: new Date(Date.now() - 1000 * 60 * 60),
        icon: 'fa fa-database',
        color: 'success'
      }
    ];
  }

  getTimeAgo(date: Date): string {
    const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
    return `${Math.floor(seconds / 86400)} days ago`;
  }
}
