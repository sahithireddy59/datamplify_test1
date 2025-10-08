import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgxPaginationModule } from 'ngx-pagination';

@Component({
  selector: 'app-admin-logs',
  standalone: true,
  imports: [CommonModule, FormsModule, NgxPaginationModule],
  templateUrl: './admin-logs.component.html',
  styleUrl: './admin-logs.component.scss'
})
export class AdminLogsComponent implements OnInit {
  logs: any[] = [];
  filteredLogs: any[] = [];
  searchTerm = '';
  selectedType = 'all';
  page = 1;
  pageSize = 10;

  logTypes = [
    { value: 'all', label: 'All Logs' },
    { value: 'user', label: 'User Activity' },
    { value: 'system', label: 'System Events' },
    { value: 'error', label: 'Errors' },
    { value: 'security', label: 'Security' }
  ];

  ngOnInit() {
    this.loadLogs();
  }

  loadLogs() {
    // Mock data - replace with actual API call
    this.logs = [
      {
        id: 1,
        type: 'user',
        user: 'admin@example.com',
        action: 'User Login',
        details: 'Successful login from IP 192.168.1.100',
        timestamp: new Date(Date.now() - 1000 * 60 * 5),
        severity: 'info'
      },
      {
        id: 2,
        type: 'user',
        user: 'john.doe@example.com',
        action: 'FlowBoard Created',
        details: 'Created new FlowBoard: Customer ETL',
        timestamp: new Date(Date.now() - 1000 * 60 * 15),
        severity: 'info'
      },
      {
        id: 3,
        type: 'error',
        user: 'system',
        action: 'Database Connection Failed',
        details: 'Failed to connect to PostgreSQL database',
        timestamp: new Date(Date.now() - 1000 * 60 * 30),
        severity: 'error'
      },
      {
        id: 4,
        type: 'security',
        user: 'admin@example.com',
        action: 'Role Permission Changed',
        details: 'Updated permissions for Data Analyst role',
        timestamp: new Date(Date.now() - 1000 * 60 * 45),
        severity: 'warning'
      },
      {
        id: 5,
        type: 'system',
        user: 'system',
        action: 'Backup Completed',
        details: 'Database backup completed successfully',
        timestamp: new Date(Date.now() - 1000 * 60 * 60),
        severity: 'success'
      }
    ];
    this.filterLogs();
  }

  filterLogs() {
    this.filteredLogs = this.logs.filter(log => {
      const matchesType = this.selectedType === 'all' || log.type === this.selectedType;
      const matchesSearch = !this.searchTerm || 
        log.action.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        log.details.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        log.user.toLowerCase().includes(this.searchTerm.toLowerCase());
      return matchesType && matchesSearch;
    });
  }

  getSeverityClass(severity: string): string {
    const classes: any = {
      'info': 'badge-info',
      'success': 'badge-success',
      'warning': 'badge-warning',
      'error': 'badge-danger'
    };
    return classes[severity] || 'badge-secondary';
  }

  getTypeIcon(type: string): string {
    const icons: any = {
      'user': 'fa-user',
      'system': 'fa-server',
      'error': 'fa-exclamation-triangle',
      'security': 'fa-shield-alt'
    };
    return icons[type] || 'fa-info-circle';
  }
}
