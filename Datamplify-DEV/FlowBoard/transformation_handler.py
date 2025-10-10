"""
Transformation Handler - All 5 transformations work with any datasource
"""


class TransformationHandler:
    """
    Generates code for all transformations (Rank, Router, Union, Normalizer, UpdateStrategy)
    Works with any datasource type
    """
    
    @staticmethod
    def generate_rank(node, input_df):
        """
        Generate Rank transformation
        Works with: All databases and file types
        """
        rank_type = node.get('rankType', 'DENSE')
        rank_col = node.get('rankColName', 'rank')
        sort_cols = node.get('sortColumns', [])
        records = node.get('records', 'ALL')
        
        if not sort_cols:
            return f"# Rank: No sort columns specified\ndf_{node['id']} = {input_df}\n"
        
        sort_by = [col['column'] for col in sort_cols]
        ascending = [col.get('order', 'ASC') == 'ASC' for col in sort_cols]
        
        code = f"""
# Rank Transformation
df_{node['id']} = {input_df}.copy()
df_{node['id']}['{rank_col}'] = df_{node['id']}.sort_values(
    by={sort_by},
    ascending={ascending}
).rank(method='{rank_type.lower()}')
"""
        
        # Apply record limit if specified
        if records != 'ALL' and str(records).isdigit():
            code += f"""
# Limit to top {records} records
df_{node['id']} = df_{node['id']}.nsmallest({records}, '{rank_col}')
"""
        
        return code
    
    
    @staticmethod
    def generate_router(node, input_df):
        """
        Generate Router transformation
        Works with: All databases and file types
        """
        conditions = node.get('conditions', [])
        
        if not conditions:
            return f"# Router: No conditions specified\ndf_{node['id']} = {input_df}\n"
        
        code = f"# Router Transformation\n"
        
        for i, cond in enumerate(conditions):
            condition = cond.get('condition', '')
            output_name = cond.get('outputName', f'output_{i}')
            
            if condition:
                code += f"""
# Route {i+1}: {output_name}
df_{output_name} = {input_df}[{input_df}.eval('{condition}')].copy()
"""
        
        # Default route (records that don't match any condition)
        code += f"""
# Default route (unmatched records)
df_{node['id']}_default = {input_df}.copy()
"""
        
        return code
    
    
    @staticmethod
    def generate_union(node, input_dfs):
        """
        Generate Union transformation
        Works with: All databases and file types
        """
        union_type = node.get('unionType', 'UNION_ALL')
        column_mappings = node.get('columnMappings', [])
        
        if not input_dfs or len(input_dfs) < 2:
            return f"# Union: Need at least 2 input dataframes\n"
        
        # Apply column mappings if specified
        if column_mappings:
            code = f"# Union Transformation with column mapping\n"
            for i, df in enumerate(input_dfs):
                code += f"""
# Rename columns for {df}
{df}_mapped = {df}.copy()
"""
                for mapping in column_mappings:
                    if f'source{i+1}Column' in mapping and 'targetColumn' in mapping:
                        code += f"{df}_mapped = {df}_mapped.rename(columns={{'{mapping[f'source{i+1}Column']}': '{mapping['targetColumn']}'}})\n"
            
            mapped_dfs = [f"{df}_mapped" for df in input_dfs]
        else:
            mapped_dfs = input_dfs
        
        # Union operation
        if union_type == 'UNION_ALL':
            code += f"""
# Union All (keep duplicates)
df_{node['id']} = pd.concat([{', '.join(mapped_dfs)}], ignore_index=True)
"""
        else:
            code += f"""
# Union (remove duplicates)
df_{node['id']} = pd.concat([{', '.join(mapped_dfs)}], ignore_index=True).drop_duplicates()
"""
        
        return code
    
    
    @staticmethod
    def generate_normalizer(node, input_df):
        """
        Generate Normalizer transformation
        Works with: All databases and file types
        """
        pivot_col = node.get('pivotColumn', '')
        group_by_cols = node.get('groupByColumns', [])
        value_cols = node.get('valueColumns', [])
        output_col = node.get('outputColumn', 'value')
        
        if not pivot_col:
            return f"# Normalizer: No pivot column specified\ndf_{node['id']} = {input_df}\n"
        
        # Use melt to normalize data
        id_vars = group_by_cols if group_by_cols else []
        value_vars = value_cols if value_cols else [pivot_col]
        
        code = f"""
# Normalizer Transformation
df_{node['id']} = {input_df}.melt(
    id_vars={id_vars},
    value_vars={value_vars},
    var_name='{pivot_col}_attribute',
    value_name='{output_col}'
)
"""
        
        return code
    
    
    @staticmethod
    def generate_update_strategy(node, source_df, target_df):
        """
        Generate UpdateStrategy transformation
        Works with: All databases and file types
        """
        strategy = node.get('strategy', 'INSERT')
        join_keys = node.get('joinKeys', [])
        update_mappings = node.get('updateMappings', [])
        
        if strategy == 'INSERT':
            # Simple insert - just pass through source data
            code = f"""
# Update Strategy: INSERT
df_{node['id']} = {source_df}.copy()
"""
        
        elif strategy == 'UPDATE':
            # Update existing records
            if not join_keys:
                return f"# Update Strategy: UPDATE requires join keys\ndf_{node['id']} = {source_df}\n"
            
            code = f"""
# Update Strategy: UPDATE
df_{node['id']} = {target_df}.copy()
df_{node['id']}.set_index({join_keys}, inplace=True)
{source_df}_indexed = {source_df}.set_index({join_keys})

# Update matching records
df_{node['id']}.update({source_df}_indexed)
df_{node['id']}.reset_index(inplace=True)
"""
        
        elif strategy == 'UPSERT':
            # Insert new records and update existing ones
            if not join_keys:
                return f"# Update Strategy: UPSERT requires join keys\ndf_{node['id']} = {source_df}\n"
            
            code = f"""
# Update Strategy: UPSERT (Insert + Update)
df_{node['id']} = pd.concat([{target_df}, {source_df}]).drop_duplicates(
    subset={join_keys},
    keep='last'
).reset_index(drop=True)
"""
        
        elif strategy == 'DELETE':
            # Delete matching records from target
            if not join_keys:
                return f"# Update Strategy: DELETE requires join keys\ndf_{node['id']} = {target_df}\n"
            
            code = f"""
# Update Strategy: DELETE
# Create a key column for comparison
{target_df}['_key'] = {target_df}[{join_keys}].astype(str).agg('_'.join, axis=1)
{source_df}['_key'] = {source_df}[{join_keys}].astype(str).agg('_'.join, axis=1)

# Keep only records not in source
df_{node['id']} = {target_df}[~{target_df}['_key'].isin({source_df}['_key'])].drop('_key', axis=1)
"""
        
        else:
            code = f"""
# Update Strategy: Unknown strategy '{strategy}'
df_{node['id']} = {source_df}.copy()
"""
        
        return code
    
    
    @staticmethod
    def generate_expression(node, input_df):
        """
        Generate Expression transformation
        Works with: All databases and file types
        """
        expressions = node.get('expressions', [])
        
        if not expressions:
            return f"# Expression: No expressions specified\ndf_{node['id']} = {input_df}\n"
        
        code = f"""
# Expression Transformation
df_{node['id']} = {input_df}.copy()
"""
        
        for expr in expressions:
            output_col = expr.get('outputColumn', '')
            expression = expr.get('expression', '')
            
            if output_col and expression:
                # Handle different expression types
                if '=' in expression or '+' in expression or '-' in expression or '*' in expression or '/' in expression:
                    # Arithmetic expression
                    code += f"df_{node['id']}['{output_col}'] = df_{node['id']}.eval('{expression}')\n"
                else:
                    # Direct assignment
                    code += f"df_{node['id']}['{output_col}'] = {expression}\n"
        
        return code
    
    
    @staticmethod
    def generate_filter(node, input_df):
        """
        Generate Filter transformation
        Works with: All databases and file types
        """
        filter_condition = node.get('filterCondition', '')
        
        if not filter_condition:
            return f"# Filter: No condition specified\ndf_{node['id']} = {input_df}\n"
        
        code = f"""
# Filter Transformation
df_{node['id']} = {input_df}[{input_df}.eval('{filter_condition}')].copy()
"""
        
        return code
    
    
    @staticmethod
    def generate_joiner(node, input_dfs):
        """
        Generate Joiner transformation
        Works with: All databases and file types
        """
        join_type = node.get('joinType', 'INNER').lower()
        join_keys = node.get('joinKeys', [])
        
        if not input_dfs or len(input_dfs) < 2:
            return f"# Joiner: Need at least 2 input dataframes\n"
        
        if not join_keys:
            return f"# Joiner: No join keys specified\ndf_{node['id']} = {input_dfs[0]}\n"
        
        left_df = input_dfs[0]
        right_df = input_dfs[1]
        
        # Extract left and right keys
        left_keys = [jk.get('leftKey', '') for jk in join_keys if jk.get('leftKey')]
        right_keys = [jk.get('rightKey', '') for jk in join_keys if jk.get('rightKey')]
        
        # Map join types
        join_type_map = {
            'inner': 'inner',
            'left': 'left',
            'right': 'right',
            'outer': 'outer',
            'full': 'outer',
            'cross': 'cross'
        }
        
        pandas_join_type = join_type_map.get(join_type, 'inner')
        
        code = f"""
# Joiner Transformation ({join_type.upper()})
df_{node['id']} = {left_df}.merge(
    {right_df},
    left_on={left_keys},
    right_on={right_keys},
    how='{pandas_join_type}',
    suffixes=('_left', '_right')
)
"""
        
        return code
    
    
    @staticmethod
    def generate_rollup(node, input_df):
        """
        Generate Rollup (Aggregation) transformation
        Works with: All databases and file types
        """
        group_by_cols = node.get('groupByColumns', [])
        aggregations = node.get('aggregations', [])
        
        if not group_by_cols:
            return f"# Rollup: No group by columns specified\ndf_{node['id']} = {input_df}\n"
        
        if not aggregations:
            return f"# Rollup: No aggregations specified\ndf_{node['id']} = {input_df}\n"
        
        code = f"""
# Rollup (Aggregation) Transformation
"""
        
        # Build aggregation dictionary
        agg_dict = {}
        for agg in aggregations:
            column = agg.get('column', '')
            function = agg.get('function', 'sum').lower()
            output_name = agg.get('outputName', f'{column}_{function}')
            
            if column:
                if column not in agg_dict:
                    agg_dict[column] = []
                agg_dict[column].append((function, output_name))
        
        # Generate aggregation code
        code += f"df_{node['id']} = {input_df}.groupby({group_by_cols}).agg({{\n"
        
        for col, funcs in agg_dict.items():
            for func, output_name in funcs:
                code += f"    '{col}': ('{func}', '{output_name}'),\n"
        
        code += "}).reset_index()\n"
        
        # Flatten column names if needed
        code += f"""
# Flatten multi-level column names if any
if isinstance(df_{node['id']}.columns, pd.MultiIndex):
    df_{node['id']}.columns = ['_'.join(col).strip('_') for col in df_{node['id']}.columns.values]
"""
        
        return code
    
    
    @staticmethod
    def generate_transformation(node, input_dfs):
        """
        Main method to generate any transformation (9 total)
        """
        node_type = node.get('type', '').lower()
        
        if node_type == 'rank':
            return TransformationHandler.generate_rank(node, input_dfs[0] if input_dfs else 'df')
        
        elif node_type == 'router':
            return TransformationHandler.generate_router(node, input_dfs[0] if input_dfs else 'df')
        
        elif node_type == 'union':
            return TransformationHandler.generate_union(node, input_dfs)
        
        elif node_type == 'normalizer':
            return TransformationHandler.generate_normalizer(node, input_dfs[0] if input_dfs else 'df')
        
        elif node_type == 'updatestrategy':
            source_df = input_dfs[0] if len(input_dfs) > 0 else 'df_source'
            target_df = input_dfs[1] if len(input_dfs) > 1 else 'df_target'
            return TransformationHandler.generate_update_strategy(node, source_df, target_df)
        
        elif node_type == 'expression':
            return TransformationHandler.generate_expression(node, input_dfs[0] if input_dfs else 'df')
        
        elif node_type == 'filter':
            return TransformationHandler.generate_filter(node, input_dfs[0] if input_dfs else 'df')
        
        elif node_type == 'joiner':
            return TransformationHandler.generate_joiner(node, input_dfs)
        
        elif node_type == 'rollup':
            return TransformationHandler.generate_rollup(node, input_dfs[0] if input_dfs else 'df')
        
        else:
            return f"# Unknown transformation type: {node_type}\n"
