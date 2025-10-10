import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GlobalParametersService, GlobalParameter, CSVLoadConfig } from '../../../services/global-parameters.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-global-parameters',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './global-parameters.component.html',
  styleUrl: './global-parameters.component.scss'
})
export class GlobalParametersComponent implements OnInit {
  // Tab management
  activeTab: 'parameters' | 'direct-load' | 'indirect-load' = 'parameters';
  
  // Global Parameters
  globalParameters: GlobalParameter[] = [];
  systemParameters: GlobalParameter[] = [];
  userParameters: GlobalParameter[] = [];
  filteredParameters: GlobalParameter[] = [];
  selectedCategory: string = 'ALL';
  
  // CSV Load Configurations
  directLoadConfigs: CSVLoadConfig[] = [];
  indirectLoadConfigs: CSVLoadConfig[] = [];
  
  // Form states
  showParameterForm: boolean = false;
  showDirectLoadForm: boolean = false;
  showIndirectLoadForm: boolean = false;
  
  isEditMode: boolean = false;
  
  // Current editing objects
  currentParameter: GlobalParameter = this.getEmptyParameter();
  currentDirectConfig: CSVLoadConfig = this.getEmptyDirectConfig();
  currentIndirectConfig: CSVLoadConfig = this.getEmptyIndirectConfig();
  
  // Loading states
  isLoading: boolean = false;
  
  // Dropdown options
  parameterTypes = [
    { value: 'STRING', label: 'String' },
    { value: 'INTEGER', label: 'Integer' },
    { value: 'BOOLEAN', label: 'Boolean' },
    { value: 'PATH', label: 'File Path' },
    { value: 'JSON', label: 'JSON Object' }
  ];
  
  categories = [
    { value: 'DIRECT_LOAD', label: 'Direct Load' },
    { value: 'INDIRECT_LOAD', label: 'Indirect Load' },
    { value: 'GENERAL', label: 'General' }
  ];
  
  errorHandlingOptions = [
    { value: 'SKIP', label: 'Skip Errors' },
    { value: 'ABORT', label: 'Abort on Error' },
    { value: 'LOG', label: 'Log and Continue' }
  ];
  
  encodingOptions = ['utf-8', 'utf-16', 'ascii', 'iso-8859-1', 'windows-1252'];
  delimiterOptions = [',', ';', '|', '\t', ' '];

  constructor(
    private globalParamsService: GlobalParametersService,
    private toastr: ToastrService
  ) {}

  ngOnInit(): void {
    this.loadAllData();
  }

  // ==================== Data Loading ====================
  
  loadAllData(): void {
    this.loadGlobalParameters();
    this.loadDirectLoadConfigs();
    this.loadIndirectLoadConfigs();
  }

  loadGlobalParameters(): void {
    this.isLoading = true;
    this.globalParamsService.getGlobalParameters().subscribe({
      next: (response) => {
        this.globalParameters = response.data;
        
        // Separate system and user parameters
        this.systemParameters = this.globalParameters.filter((p: any) => p.is_system === true);
        this.userParameters = this.globalParameters.filter((p: any) => p.is_system !== true);
        
        this.filterParameters();
        this.isLoading = false;
      },
      error: (error) => {
        this.toastr.error('Failed to load global parameters', 'Error');
        this.isLoading = false;
      }
    });
  }

  loadDirectLoadConfigs(): void {
    this.globalParamsService.getCSVLoadConfigs('DIRECT').subscribe({
      next: (response) => {
        this.directLoadConfigs = response.data;
      },
      error: (error) => {
        this.toastr.error('Failed to load direct load configurations', 'Error');
      }
    });
  }

  loadIndirectLoadConfigs(): void {
    this.globalParamsService.getCSVLoadConfigs('INDIRECT').subscribe({
      next: (response) => {
        this.indirectLoadConfigs = response.data;
      },
      error: (error) => {
        this.toastr.error('Failed to load indirect load configurations', 'Error');
      }
    });
  }

  // ==================== Tab Management ====================
  
  switchTab(tab: 'parameters' | 'direct-load' | 'indirect-load'): void {
    this.activeTab = tab;
    this.closeAllForms();
  }

  // ==================== Global Parameters ====================
  
  filterParameters(): void {
    if (this.selectedCategory === 'ALL') {
      this.filteredParameters = this.globalParameters;
    } else {
      this.filteredParameters = this.globalParameters.filter(
        p => p.category === this.selectedCategory
      );
    }
  }

  onCategoryChange(): void {
    this.filterParameters();
  }

  openParameterForm(parameter?: GlobalParameter): void {
    if (parameter) {
      this.currentParameter = { ...parameter };
      this.isEditMode = true;
    } else {
      this.currentParameter = this.getEmptyParameter();
      this.isEditMode = false;
    }
    this.showParameterForm = true;
  }

  saveParameter(): void {
    if (!this.validateParameter()) return;

    if (this.isEditMode) {
      this.globalParamsService.updateGlobalParameter(this.currentParameter).subscribe({
        next: (response) => {
          this.toastr.success('Parameter updated successfully', 'Success');
          this.loadGlobalParameters();
          this.closeAllForms();
        },
        error: (error) => {
          this.toastr.error(error.error?.message || 'Failed to update parameter', 'Error');
        }
      });
    } else {
      this.globalParamsService.createGlobalParameter(this.currentParameter).subscribe({
        next: (response) => {
          this.toastr.success('Parameter created successfully', 'Success');
          this.loadGlobalParameters();
          this.closeAllForms();
        },
        error: (error) => {
          this.toastr.error(error.error?.message || 'Failed to create parameter', 'Error');
        }
      });
    }
  }

  deleteParameter(id: string): void {
    if (!confirm('Are you sure you want to delete this parameter?')) return;

    this.globalParamsService.deleteGlobalParameter(id).subscribe({
      next: (response) => {
        this.toastr.success('Parameter deleted successfully', 'Success');
        this.loadGlobalParameters();
      },
      error: (error) => {
        this.toastr.error('Failed to delete parameter', 'Error');
      }
    });
  }

  validateParameter(): boolean {
    if (!this.currentParameter.parameter_name) {
      this.toastr.warning('Parameter name is required', 'Validation');
      return false;
    }
    if (!this.currentParameter.parameter_value) {
      this.toastr.warning('Parameter value is required', 'Validation');
      return false;
    }
    return true;
  }

  // ==================== Direct Load Configuration ====================
  
  openDirectLoadForm(config?: CSVLoadConfig): void {
    if (config) {
      this.currentDirectConfig = { ...config };
      this.isEditMode = true;
    } else {
      this.currentDirectConfig = this.getEmptyDirectConfig();
      this.isEditMode = false;
    }
    this.showDirectLoadForm = true;
  }

  saveDirectLoadConfig(): void {
    const validation = this.globalParamsService.validateConfig(this.currentDirectConfig);
    if (!validation.valid) {
      validation.errors.forEach(error => this.toastr.warning(error, 'Validation'));
      return;
    }

    if (this.isEditMode) {
      this.globalParamsService.updateCSVLoadConfig(this.currentDirectConfig).subscribe({
        next: (response) => {
          this.toastr.success('Configuration updated successfully', 'Success');
          this.loadDirectLoadConfigs();
          this.closeAllForms();
        },
        error: (error) => {
          this.toastr.error('Failed to update configuration', 'Error');
        }
      });
    } else {
      this.globalParamsService.createCSVLoadConfig(this.currentDirectConfig).subscribe({
        next: (response) => {
          this.toastr.success('Configuration created successfully', 'Success');
          this.loadDirectLoadConfigs();
          this.closeAllForms();
        },
        error: (error) => {
          this.toastr.error('Failed to create configuration', 'Error');
        }
      });
    }
  }

  deleteDirectLoadConfig(id: string): void {
    if (!confirm('Are you sure you want to delete this configuration?')) return;

    this.globalParamsService.deleteCSVLoadConfig(id).subscribe({
      next: (response) => {
        this.toastr.success('Configuration deleted successfully', 'Success');
        this.loadDirectLoadConfigs();
      },
      error: (error) => {
        this.toastr.error('Failed to delete configuration', 'Error');
      }
    });
  }

  setAsDefaultDirect(config: CSVLoadConfig): void {
    const updatedConfig = { ...config, is_default: true };
    this.globalParamsService.updateCSVLoadConfig(updatedConfig).subscribe({
      next: (response) => {
        this.toastr.success('Set as default configuration', 'Success');
        this.loadDirectLoadConfigs();
      },
      error: (error) => {
        this.toastr.error('Failed to set as default', 'Error');
      }
    });
  }

  // ==================== Indirect Load Configuration ====================
  
  openIndirectLoadForm(config?: CSVLoadConfig): void {
    if (config) {
      this.currentIndirectConfig = { ...config };
      this.isEditMode = true;
    } else {
      this.currentIndirectConfig = this.getEmptyIndirectConfig();
      this.isEditMode = false;
    }
    this.showIndirectLoadForm = true;
  }

  saveIndirectLoadConfig(): void {
    const validation = this.globalParamsService.validateConfig(this.currentIndirectConfig);
    if (!validation.valid) {
      validation.errors.forEach(error => this.toastr.warning(error, 'Validation'));
      return;
    }

    if (this.isEditMode) {
      this.globalParamsService.updateCSVLoadConfig(this.currentIndirectConfig).subscribe({
        next: (response) => {
          this.toastr.success('Configuration updated successfully', 'Success');
          this.loadIndirectLoadConfigs();
          this.closeAllForms();
        },
        error: (error) => {
          this.toastr.error('Failed to update configuration', 'Error');
        }
      });
    } else {
      this.globalParamsService.createCSVLoadConfig(this.currentIndirectConfig).subscribe({
        next: (response) => {
          this.toastr.success('Configuration created successfully', 'Success');
          this.loadIndirectLoadConfigs();
          this.closeAllForms();
        },
        error: (error) => {
          this.toastr.error('Failed to create configuration', 'Error');
        }
      });
    }
  }

  deleteIndirectLoadConfig(id: string): void {
    if (!confirm('Are you sure you want to delete this configuration?')) return;

    this.globalParamsService.deleteCSVLoadConfig(id).subscribe({
      next: (response) => {
        this.toastr.success('Configuration deleted successfully', 'Success');
        this.loadIndirectLoadConfigs();
      },
      error: (error) => {
        this.toastr.error('Failed to delete configuration', 'Error');
      }
    });
  }

  setAsDefaultIndirect(config: CSVLoadConfig): void {
    const updatedConfig = { ...config, is_default: true };
    this.globalParamsService.updateCSVLoadConfig(updatedConfig).subscribe({
      next: (response) => {
        this.toastr.success('Set as default configuration', 'Success');
        this.loadIndirectLoadConfigs();
      },
      error: (error) => {
        this.toastr.error('Failed to set as default', 'Error');
      }
    });
  }

  // ==================== Helper Methods ====================
  
  closeAllForms(): void {
    this.showParameterForm = false;
    this.showDirectLoadForm = false;
    this.showIndirectLoadForm = false;
    this.isEditMode = false;
  }

  getEmptyParameter(): GlobalParameter {
    return {
      parameter_name: '',
      parameter_value: '',
      parameter_type: 'STRING',
      category: 'GENERAL',
      description: '',
      is_active: true
    };
  }

  getEmptyDirectConfig(): CSVLoadConfig {
    return this.globalParamsService.getDefaultDirectLoadConfig();
  }

  getEmptyIndirectConfig(): CSVLoadConfig {
    return this.globalParamsService.getDefaultIndirectLoadConfig();
  }

  // Add/Remove null values
  addNullValue(config: CSVLoadConfig): void {
    if (!config.null_values) {
      config.null_values = [];
    }
    config.null_values.push('');
  }

  removeNullValue(config: CSVLoadConfig, index: number): void {
    if (config.null_values) {
      config.null_values.splice(index, 1);
    }
  }

  trackByIndex(index: number): number {
    return index;
  }
}
