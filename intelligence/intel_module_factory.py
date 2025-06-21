class IntelligenceModuleFactory:
    """Factory for creating intelligence modules"""
    
    def __init__(self, keywords_config: Dict[str, Any], modules_config: Dict[str, Any], logger=None):
        self.keywords_config = keywords_config
        self.modules_config = modules_config
        self.logger = logger
        
        # Module registry
        self.module_registry = {
            'narcotics': NarcoticsIntelligenceModule,
            'financial_fraud': FinancialFraudModule,
            'human_trafficking': HumanTraffickingModule,
            'domestic_violence': DomesticViolenceModule
        }
    
    def create_module(self, module_name: str) -> Optional[BaseIntelligenceModule]:
        """Create an intelligence module by name"""
        if module_name not in self.module_registry:
            if self.logger:
                self.logger.log_action("MODULE_ERROR", f"Unknown module: {module_name}")
            return None
        
        module_class = self.module_registry[module_name]
        keywords = self.keywords_config.get(module_name, {})
        config = self.modules_config.get(module_name, {})
        
        try:
            return module_class(keywords, config, self.logger)
        except Exception as e:
            if self.logger:
                self.logger.log_action("MODULE_CREATE_ERROR", f"Error creating {module_name}: {str(e)}")
            return None
    
    def get_available_modules(self) -> List[str]:
        """Get list of available module names"""
        return list(self.module_registry.keys())
    
    def register_module(self, name: str, module_class: type):
        """Register a new intelligence module"""
        self.module_registry[name] = module_class
        if self.logger:
            self.logger.log_action("MODULE_REGISTERED", f"Registered new module: {name}")
    
    def get_module_info(self, module_name: str) -> Dict[str, Any]:
        """Get information about a specific module"""
        if module_name not in self.module_registry:
            return {'error': f'Module {module_name} not found'}
        
        module_class = self.module_registry[module_name]
        keywords = self.keywords_config.get(module_name, {})
        config = self.modules_config.get(module_name, {})
        
        return {
            'name': module_name,
            'class': module_class.__name__,
            'enabled': config.get('enabled', True),
            'keyword_categories': list(keywords.keys()) if keywords else [],
            'total_keywords': sum(len(kw_list) for kw_list in keywords.values() if isinstance(kw_list, list)),
            'risk_weights': config.get('risk_weights', {}),
            'description': module_class.__doc__ or 'No description available'
        }
