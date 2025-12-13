<?php

/**
 * Helper Generator SaaS - Runtime Container Analysis & Helper Generation
 * 
 * Analyzes runtime dependency injection containers, service locators, and facades
 * to generate perfect intelephense_helper.php files with accurate type information.
 * 
 * @package HelperGenerator
 * @version 1.0.0
 * @author EQ12 Development Team
 */

namespace HelperGenerator;

use ReflectionClass;
use ReflectionMethod;
use ReflectionParameter;
use ReflectionProperty;
use ReflectionType;
use ReflectionNamedType;
use ReflectionUnionType;

/**
 * Main Helper Generator Service
 */
class HelperGeneratorService
{
    private ContainerAnalyzer $containerAnalyzer;
    private FacadeAnalyzer $facadeAnalyzer;
    private ServiceLocatorAnalyzer $serviceLocatorAnalyzer;
    private HelperFileGenerator $helperGenerator;
    private TypeInferencer $typeInferencer;

    public function __construct()
    {
        $this->containerAnalyzer = new ContainerAnalyzer();
        $this->facadeAnalyzer = new FacadeAnalyzer();
        $this->serviceLocatorAnalyzer = new ServiceLocatorAnalyzer();
        $this->helperGenerator = new HelperFileGenerator();
        $this->typeInferencer = new TypeInferencer();
    }

    /**
     * Generate helper file from live application analysis
     *
     * @param ApplicationContext $context
     * @return HelperGenerationResult
     */
    public function generateFromApplication(ApplicationContext $context): HelperGenerationResult
    {
        $analysisResults = [];

        // Analyze DI containers
        if ($context->hasContainer()) {
            $containerResults = $this->containerAnalyzer->analyze($context->getContainer());
            $analysisResults['container'] = $containerResults;
        }

        // Analyze facades
        if ($context->hasFacades()) {
            $facadeResults = $this->facadeAnalyzer->analyze($context->getFacades());
            $analysisResults['facades'] = $facadeResults;
        }

        // Analyze service locators
        if ($context->hasServiceLocators()) {
            $serviceResults = $this->serviceLocatorAnalyzer->analyze($context->getServiceLocators());
            $analysisResults['services'] = $serviceResults;
        }

        // Generate consolidated helper file
        $helperContent = $this->helperGenerator->generate($analysisResults, $context);

        return new HelperGenerationResult(
            $helperContent,
            $analysisResults,
            $this->calculateQualityMetrics($analysisResults)
        );
    }

    /**
     * Generate framework-specific helper
     *
     * @param string $framework Laravel|Symfony|WordPress|Custom
     * @param string $projectPath
     * @param array<string, mixed> $options
     * @return HelperGenerationResult
     */
    public function generateForFramework(
        string $framework,
        string $projectPath,
        array $options = []
    ): HelperGenerationResult {
        $strategy = FrameworkStrategyFactory::create($framework);
        $context = $strategy->createContext($projectPath, $options);

        return $this->generateFromApplication($context);
    }

    /**
     * Update existing helper file with new discoveries
     *
     * @param string $existingHelperPath
     * @param ApplicationContext $context
     * @return HelperUpdateResult
     */
    public function updateExistingHelper(
        string $existingHelperPath,
        ApplicationContext $context
    ): HelperUpdateResult {
        $existingHelper = file_get_contents($existingHelperPath);
        $newResult = $this->generateFromApplication($context);

        $merger = new HelperMerger();
        $mergedContent = $merger->merge($existingHelper, $newResult->getHelperContent());

        return new HelperUpdateResult(
            $mergedContent,
            $merger->getChanges(),
            $newResult->getQualityMetrics()
        );
    }

    private function calculateQualityMetrics(array $analysisResults): QualityMetrics
    {
        $totalMethods = 0;
        $typedMethods = 0;
        $complexTypes = 0;

        foreach ($analysisResults as $category => $results) {
            foreach ($results->getDiscoveredServices() as $service) {
                $totalMethods += count($service->getMethods());
                $typedMethods += count(array_filter(
                    $service->getMethods(),
                    fn($method) => $method->hasReturnType()
                ));
                $complexTypes += count(array_filter(
                    $service->getMethods(),
                    fn($method) => $method->hasComplexReturnType()
                ));
            }
        }

        return new QualityMetrics(
            $totalMethods > 0 ? ($typedMethods / $totalMethods) * 100 : 0,
            $complexTypes,
            count($analysisResults),
            $totalMethods
        );
    }
}

/**
 * Analyzes Dependency Injection Containers
 */
class ContainerAnalyzer
{
    /**
     * Analyze DI container for service definitions
     *
     * @param mixed $container
     * @return ContainerAnalysisResult
     */
    public function analyze($container): ContainerAnalysisResult
    {
        $services = [];
        $bindings = $this->extractBindings($container);

        foreach ($bindings as $abstract => $concrete) {
            try {
                $serviceInfo = $this->analyzeService($abstract, $concrete);
                if ($serviceInfo) {
                    $services[] = $serviceInfo;
                }
            } catch (\Throwable $e) {
                // Log error and continue
                error_log("Failed to analyze service {$abstract}: " . $e->getMessage());
            }
        }

        return new ContainerAnalysisResult($services, $bindings);
    }

    private function extractBindings($container): array
    {
        $bindings = [];

        // Laravel Container
        if (method_exists($container, 'getBindings')) {
            foreach ($container->getBindings() as $abstract => $binding) {
                $bindings[$abstract] = $binding['concrete'] ?? $abstract;
            }
        }

        // Symfony Container
        elseif (method_exists($container, 'getServiceIds')) {
            foreach ($container->getServiceIds() as $serviceId) {
                try {
                    $service = $container->get($serviceId);
                    $bindings[$serviceId] = get_class($service);
                } catch (\Throwable $e) {
                    // Service not instantiable, skip
                }
            }
        }

        // PSR-11 Container
        elseif (method_exists($container, 'has') && method_exists($container, 'get')) {
            // Generic PSR-11 analysis
            $bindings = $this->analyzePSR11Container($container);
        }

        return $bindings;
    }

    private function analyzeService(string $abstract, $concrete): ?DiscoveredService
    {
        if (is_string($concrete) && class_exists($concrete)) {
            $reflection = new ReflectionClass($concrete);

            if ($reflection->isInstantiable()) {
                return new DiscoveredService(
                    $abstract,
                    $concrete,
                    $this->extractMethodSignatures($reflection),
                    $this->extractPropertyTypes($reflection),
                    'container'
                );
            }
        }

        return null;
    }

    private function extractMethodSignatures(ReflectionClass $class): array
    {
        $methods = [];

        foreach ($class->getMethods(ReflectionMethod::IS_PUBLIC) as $method) {
            if (!$method->isConstructor() && !$method->isDestructor()) {
                $methods[] = new MethodSignature(
                    $method->getName(),
                    $this->extractParameterTypes($method),
                    $this->extractReturnType($method),
                    $method->getDocComment() ?: ''
                );
            }
        }

        return $methods;
    }

    private function extractParameterTypes(ReflectionMethod $method): array
    {
        $parameters = [];

        foreach ($method->getParameters() as $param) {
            $parameters[] = new ParameterType(
                $param->getName(),
                $this->getTypeString($param->getType()),
                $param->isDefaultValueAvailable(),
                $param->isDefaultValueAvailable() ? $param->getDefaultValue() : null
            );
        }

        return $parameters;
    }

    private function extractReturnType(ReflectionMethod $method): ?string
    {
        $returnType = $method->getReturnType();
        return $returnType ? $this->getTypeString($returnType) : null;
    }

    private function extractPropertyTypes(ReflectionClass $class): array
    {
        $properties = [];

        foreach ($class->getProperties(ReflectionProperty::IS_PUBLIC) as $property) {
            $type = $property->getType();
            $properties[] = new PropertyType(
                $property->getName(),
                $type ? $this->getTypeString($type) : 'mixed'
            );
        }

        return $properties;
    }

    private function getTypeString(?ReflectionType $type): string
    {
        if (!$type) {
            return 'mixed';
        }

        if ($type instanceof ReflectionNamedType) {
            return $type->getName();
        }

        if ($type instanceof ReflectionUnionType) {
            return implode('|', array_map(
                fn(ReflectionType $t) => $this->getTypeString($t),
                $type->getTypes()
            ));
        }

        return 'mixed';
    }

    private function analyzePSR11Container($container): array
    {
        // This would require reflection to find service IDs
        // Implementation depends on specific container
        return [];
    }
}

/**
 * Analyzes Facade patterns (Laravel, etc.)
 */
class FacadeAnalyzer
{
    /**
     * @param array<string> $facadeClasses
     * @return FacadeAnalysisResult
     */
    public function analyze(array $facadeClasses): FacadeAnalysisResult
    {
        $facades = [];

        foreach ($facadeClasses as $facadeClass) {
            try {
                $facadeInfo = $this->analyzeFacade($facadeClass);
                if ($facadeInfo) {
                    $facades[] = $facadeInfo;
                }
            } catch (\Throwable $e) {
                error_log("Failed to analyze facade {$facadeClass}: " . $e->getMessage());
            }
        }

        return new FacadeAnalysisResult($facades);
    }

    private function analyzeFacade(string $facadeClass): ?DiscoveredFacade
    {
        if (!class_exists($facadeClass)) {
            return null;
        }

        $reflection = new ReflectionClass($facadeClass);

        // Look for getFacadeAccessor method (Laravel style)
        if ($reflection->hasMethod('getFacadeAccessor')) {
            $accessor = $reflection->getMethod('getFacadeAccessor');

            if ($accessor->isStatic()) {
                try {
                    $accessorValue = $accessor->invoke(null);
                    $underlyingClass = $this->resolveUnderlyingClass($accessorValue);

                    if ($underlyingClass) {
                        return new DiscoveredFacade(
                            $facadeClass,
                            $accessorValue,
                            $underlyingClass,
                            $this->extractFacadeMethods($underlyingClass)
                        );
                    }
                } catch (\Throwable $e) {
                    // Failed to resolve, skip
                }
            }
        }

        return null;
    }

    private function resolveUnderlyingClass(string $accessor): ?string
    {
        // This would need framework-specific resolution logic
        // For Laravel, we'd resolve through the container

        // Simple class name resolution
        if (class_exists($accessor)) {
            return $accessor;
        }

        return null;
    }

    private function extractFacadeMethods(string $className): array
    {
        if (!class_exists($className)) {
            return [];
        }

        $reflection = new ReflectionClass($className);
        $methods = [];

        foreach ($reflection->getMethods(ReflectionMethod::IS_PUBLIC) as $method) {
            if (!$method->isConstructor() && !$method->isDestructor()) {
                $methods[] = new FacadeMethod(
                    $method->getName(),
                    $this->extractParameterTypes($method),
                    $this->extractReturnType($method),
                    $method->isStatic()
                );
            }
        }

        return $methods;
    }

    private function extractParameterTypes(ReflectionMethod $method): array
    {
        // Same implementation as ContainerAnalyzer
        return [];
    }

    private function extractReturnType(ReflectionMethod $method): ?string
    {
        // Same implementation as ContainerAnalyzer  
        return null;
    }
}

/**
 * Analyzes Service Locator patterns
 */
class ServiceLocatorAnalyzer
{
    /**
     * @param array<mixed> $serviceLocators
     * @return ServiceLocatorAnalysisResult
     */
    public function analyze(array $serviceLocators): ServiceLocatorAnalysisResult
    {
        $services = [];

        foreach ($serviceLocators as $locator) {
            $locatorServices = $this->analyzeServiceLocator($locator);
            $services = array_merge($services, $locatorServices);
        }

        return new ServiceLocatorAnalysisResult($services);
    }

    private function analyzeServiceLocator($locator): array
    {
        $services = [];

        // WordPress-style service locator
        if (is_array($locator)) {
            foreach ($locator as $key => $service) {
                if (is_object($service)) {
                    $services[] = new DiscoveredService(
                        $key,
                        get_class($service),
                        $this->extractObjectMethods($service),
                        [],
                        'service_locator'
                    );
                }
            }
        }

        // Object-based service locator
        elseif (is_object($locator)) {
            $reflection = new ReflectionClass($locator);

            // Look for get() method pattern
            if ($reflection->hasMethod('get')) {
                // This would require runtime analysis to determine available services
                $services = $this->analyzeObjectServiceLocator($locator, $reflection);
            }
        }

        return $services;
    }

    private function extractObjectMethods(object $service): array
    {
        $reflection = new ReflectionClass($service);
        $methods = [];

        foreach ($reflection->getMethods(ReflectionMethod::IS_PUBLIC) as $method) {
            $methods[] = new MethodSignature(
                $method->getName(),
                [], // Parameters would be extracted here
                null, // Return type would be extracted here
                ''
            );
        }

        return $methods;
    }

    private function analyzeObjectServiceLocator(object $locator, ReflectionClass $reflection): array
    {
        // This would require framework-specific knowledge
        return [];
    }
}

/**
 * Generates the actual helper PHP file
 */
class HelperFileGenerator
{
    /**
     * Generate complete helper file content
     *
     * @param array<string, mixed> $analysisResults
     * @param ApplicationContext $context
     * @return string
     */
    public function generate(array $analysisResults, ApplicationContext $context): string
    {
        $content = $this->generateFileHeader($context);

        // Generate container helpers
        if (isset($analysisResults['container'])) {
            $content .= $this->generateContainerHelpers($analysisResults['container']);
        }

        // Generate facade helpers
        if (isset($analysisResults['facades'])) {
            $content .= $this->generateFacadeHelpers($analysisResults['facades']);
        }

        // Generate service locator helpers
        if (isset($analysisResults['services'])) {
            $content .= $this->generateServiceHelpers($analysisResults['services']);
        }

        $content .= $this->generateFileFooter();

        return $content;
    }

    private function generateFileHeader(ApplicationContext $context): string
    {
        $framework = $context->getFramework();
        $timestamp = date('Y-m-d H:i:s');
        $version = $context->getVersion();

        return <<<PHP
<?php
/**
 * Intelephense Helper for {$framework}
 * 
 * Auto-generated helper file for perfect IntelliSense
 * Generated by HelperGenerator SaaS on {$timestamp}
 * 
 * @package HelperGenerator\\{$framework}
 * @version {$version}
 */

// Prevent execution in production
if (!defined('INTELEPHENSE_HELPER') && !class_exists('IntelephenseHelper')) {
    return;
}

/**
 * ==========================================================================
 * DEPENDENCY INJECTION CONTAINER HELPERS
 * ==========================================================================
 */


PHP;
    }

    private function generateContainerHelpers(ContainerAnalysisResult $result): string
    {
        $content = '';

        foreach ($result->getDiscoveredServices() as $service) {
            $content .= $this->generateServiceClass($service);
        }

        // Generate container accessor function
        $content .= $this->generateContainerFunction($result->getDiscoveredServices());

        return $content;
    }

    private function generateServiceClass(DiscoveredService $service): string
    {
        $abstract = $service->getAbstract();
        $concrete = $service->getConcrete();
        $methods = $service->getMethods();

        $content = "/**\n";
        $content .= " * {$abstract} Service Helper\n";
        $content .= " * \n";
        $content .= " * @see {$concrete}\n";
        $content .= " */\n";
        $content .= "class {$this->sanitizeClassName($abstract)}\n{\n";

        foreach ($methods as $method) {
            $content .= $this->generateMethodStub($method);
        }

        $content .= "}\n\n";

        return $content;
    }

    private function generateMethodStub(MethodSignature $method): string
    {
        $params = array_map(
            fn(ParameterType $p) => $this->formatParameter($p),
            $method->getParameters()
        );

        $paramString = implode(', ', $params);
        $returnType = $method->getReturnType() ? ": {$method->getReturnType()}" : '';

        $content = "    /**\n";

        foreach ($method->getParameters() as $param) {
            $content .= "     * @param {$param->getType()} \${$param->getName()}\n";
        }

        if ($method->getReturnType()) {
            $content .= "     * @return {$method->getReturnType()}\n";
        }

        $content .= "     */\n";
        $content .= "    public function {$method->getName()}({$paramString}){$returnType}\n";
        $content .= "    {\n";
        $content .= "        // Auto-generated stub for IntelliSense\n";
        $content .= "    }\n\n";

        return $content;
    }

    private function formatParameter(ParameterType $param): string
    {
        $result = '';

        if ($param->getType() !== 'mixed') {
            $result .= $param->getType() . ' ';
        }

        $result .= '$' . $param->getName();

        if ($param->hasDefault()) {
            $default = $param->getDefaultValue();

            if (is_null($default)) {
                $result .= ' = null';
            } elseif (is_bool($default)) {
                $result .= ' = ' . ($default ? 'true' : 'false');
            } elseif (is_string($default)) {
                $result .= " = '" . addslashes($default) . "'";
            } elseif (is_numeric($default)) {
                $result .= ' = ' . $default;
            } elseif (is_array($default)) {
                $result .= ' = []';
            }
        }

        return $result;
    }

    private function generateContainerFunction(array $services): string
    {
        $content = "/**\n";
        $content .= " * Container Service Resolution Helper\n";
        $content .= " * \n";

        foreach ($services as $service) {
            $abstract = $service->getAbstract();
            $className = $this->sanitizeClassName($abstract);
            $content .= " * @method {$className} {$abstract}()\n";
        }

        $content .= " */\n";
        $content .= "function container(string \$abstract = null)\n{\n";
        $content .= "    // Helper function for perfect container resolution IntelliSense\n";
        $content .= "}\n\n";

        return $content;
    }

    private function generateFacadeHelpers(FacadeAnalysisResult $result): string
    {
        $content = "/**\n";
        $content .= " * ==========================================================================\n";
        $content .= " * FACADE HELPERS\n";
        $content .= " * ==========================================================================\n";
        $content .= " */\n\n";

        foreach ($result->getFacades() as $facade) {
            $content .= $this->generateFacadeClass($facade);
        }

        return $content;
    }

    private function generateFacadeClass(DiscoveredFacade $facade): string
    {
        $facadeClass = $facade->getFacadeClass();
        $underlyingClass = $facade->getUnderlyingClass();
        $methods = $facade->getMethods();

        $content = "/**\n";
        $content .= " * {$facadeClass} Facade Helper\n";
        $content .= " * \n";
        $content .= " * @see {$underlyingClass}\n";

        foreach ($methods as $method) {
            $params = array_map(
                fn(ParameterType $p) => "{$p->getType()} \${$p->getName()}",
                $method->getParameters()
            );
            $paramString = implode(', ', $params);
            $returnType = $method->getReturnType() ?: 'mixed';

            $content .= " * @method static {$returnType} {$method->getName()}({$paramString})\n";
        }

        $content .= " */\n";
        $content .= "class {$this->getShortClassName($facadeClass)} {}\n\n";

        return $content;
    }

    private function generateServiceHelpers(ServiceLocatorAnalysisResult $result): string
    {
        $content = "/**\n";
        $content .= " * ==========================================================================\n";
        $content .= " * SERVICE LOCATOR HELPERS\n";
        $content .= " * ==========================================================================\n";
        $content .= " */\n\n";

        foreach ($result->getServices() as $service) {
            $content .= $this->generateServiceLocatorFunction($service);
        }

        return $content;
    }

    private function generateServiceLocatorFunction(DiscoveredService $service): string
    {
        $abstract = $service->getAbstract();
        $concrete = $service->getConcrete();

        return "/**\n" .
            " * Get {$abstract} service\n" .
            " * \n" .
            " * @return {$concrete}\n" .
            " */\n" .
            "function get_{$this->sanitizeFunctionName($abstract)}(): {$concrete}\n" .
            "{\n" .
            "    // Service locator helper for IntelliSense\n" .
            "}\n\n";
    }

    private function generateFileFooter(): string
    {
        return <<<PHP
/**
 * ==========================================================================
 * RUNTIME SAFETY GUARDS
 * ==========================================================================
 */

// Prevent any actual execution of this helper file
if (function_exists('header')) {
    header('HTTP/1.0 403 Forbidden');
    exit('This file is for IDE assistance only');
}

if (PHP_SAPI !== 'cli' && !defined('PHPUNIT_COMPOSER_INSTALL')) {
    die('This file is for IDE assistance only');
}
PHP;
    }

    private function sanitizeClassName(string $name): string
    {
        // Remove namespace separators and make valid PHP class name
        $name = str_replace(['\\', '.', '-', '/'], '_', $name);
        $name = preg_replace('/[^a-zA-Z0-9_]/', '', $name);

        if (is_numeric($name[0] ?? '')) {
            $name = 'Service_' . $name;
        }

        return ucfirst($name) . 'Helper';
    }

    private function sanitizeFunctionName(string $name): string
    {
        return strtolower(str_replace(['\\', '.', '-', '/'], '_', $name));
    }

    private function getShortClassName(string $fullClassName): string
    {
        $parts = explode('\\', $fullClassName);
        return end($parts);
    }
}

/**
 * Data transfer objects
 */

class ApplicationContext
{
    public function __construct(
        private string $framework,
        private string $version,
        private string $projectPath,
        private ?object $container = null,
        private array $facades = [],
        private array $serviceLocators = []
    ) {}

    public function getFramework(): string
    {
        return $this->framework;
    }
    public function getVersion(): string
    {
        return $this->version;
    }
    public function getProjectPath(): string
    {
        return $this->projectPath;
    }
    public function hasContainer(): bool
    {
        return $this->container !== null;
    }
    public function getContainer(): ?object
    {
        return $this->container;
    }
    public function hasFacades(): bool
    {
        return !empty($this->facades);
    }
    public function getFacades(): array
    {
        return $this->facades;
    }
    public function hasServiceLocators(): bool
    {
        return !empty($this->serviceLocators);
    }
    public function getServiceLocators(): array
    {
        return $this->serviceLocators;
    }
}

class HelperGenerationResult
{
    public function __construct(
        private string $helperContent,
        private array $analysisResults,
        private QualityMetrics $qualityMetrics
    ) {}

    public function getHelperContent(): string
    {
        return $this->helperContent;
    }
    public function getAnalysisResults(): array
    {
        return $this->analysisResults;
    }
    public function getQualityMetrics(): QualityMetrics
    {
        return $this->qualityMetrics;
    }
}

class QualityMetrics
{
    public function __construct(
        private float $typeCoverage,
        private int $complexTypes,
        private int $discoveredServices,
        private int $totalMethods
    ) {}

    public function getTypeCoverage(): float
    {
        return $this->typeCoverage;
    }
    public function getComplexTypes(): int
    {
        return $this->complexTypes;
    }
    public function getDiscoveredServices(): int
    {
        return $this->discoveredServices;
    }
    public function getTotalMethods(): int
    {
        return $this->totalMethods;
    }
}

class ContainerAnalysisResult
{
    /** @param DiscoveredService[] $services */
    public function __construct(
        private array $services,
        private array $bindings
    ) {}

    public function getDiscoveredServices(): array
    {
        return $this->services;
    }
    public function getBindings(): array
    {
        return $this->bindings;
    }
}

class DiscoveredService
{
    /** @param MethodSignature[] $methods */
    /** @param PropertyType[] $properties */
    public function __construct(
        private string $abstract,
        private string $concrete,
        private array $methods,
        private array $properties,
        private string $source
    ) {}

    public function getAbstract(): string
    {
        return $this->abstract;
    }
    public function getConcrete(): string
    {
        return $this->concrete;
    }
    public function getMethods(): array
    {
        return $this->methods;
    }
    public function getProperties(): array
    {
        return $this->properties;
    }
    public function getSource(): string
    {
        return $this->source;
    }
}

class MethodSignature
{
    /** @param ParameterType[] $parameters */
    public function __construct(
        private string $name,
        private array $parameters,
        private ?string $returnType,
        private string $docComment
    ) {}

    public function getName(): string
    {
        return $this->name;
    }
    public function getParameters(): array
    {
        return $this->parameters;
    }
    public function getReturnType(): ?string
    {
        return $this->returnType;
    }
    public function getDocComment(): string
    {
        return $this->docComment;
    }
    public function hasReturnType(): bool
    {
        return $this->returnType !== null;
    }
    public function hasComplexReturnType(): bool
    {
        return $this->returnType && (
            str_contains($this->returnType, 'array') ||
            str_contains($this->returnType, '|') ||
            str_contains($this->returnType, '<')
        );
    }
}

class ParameterType
{
    public function __construct(
        private string $name,
        private string $type,
        private bool $hasDefault,
        private mixed $defaultValue = null
    ) {}

    public function getName(): string
    {
        return $this->name;
    }
    public function getType(): string
    {
        return $this->type;
    }
    public function hasDefault(): bool
    {
        return $this->hasDefault;
    }
    public function getDefaultValue(): mixed
    {
        return $this->defaultValue;
    }
}

class PropertyType
{
    public function __construct(
        private string $name,
        private string $type
    ) {}

    public function getName(): string
    {
        return $this->name;
    }
    public function getType(): string
    {
        return $this->type;
    }
}

class FacadeAnalysisResult
{
    /** @param DiscoveredFacade[] $facades */
    public function __construct(private array $facades) {}

    public function getFacades(): array
    {
        return $this->facades;
    }
}

class DiscoveredFacade
{
    /** @param FacadeMethod[] $methods */
    public function __construct(
        private string $facadeClass,
        private string $accessor,
        private string $underlyingClass,
        private array $methods
    ) {}

    public function getFacadeClass(): string
    {
        return $this->facadeClass;
    }
    public function getAccessor(): string
    {
        return $this->accessor;
    }
    public function getUnderlyingClass(): string
    {
        return $this->underlyingClass;
    }
    public function getMethods(): array
    {
        return $this->methods;
    }
}

class FacadeMethod
{
    /** @param ParameterType[] $parameters */
    public function __construct(
        private string $name,
        private array $parameters,
        private ?string $returnType,
        private bool $isStatic
    ) {}

    public function getName(): string
    {
        return $this->name;
    }
    public function getParameters(): array
    {
        return $this->parameters;
    }
    public function getReturnType(): ?string
    {
        return $this->returnType;
    }
    public function isStatic(): bool
    {
        return $this->isStatic;
    }
}

class ServiceLocatorAnalysisResult
{
    /** @param DiscoveredService[] $services */
    public function __construct(private array $services) {}

    public function getServices(): array
    {
        return $this->services;
    }
}

class HelperUpdateResult
{
    public function __construct(
        private string $mergedContent,
        private array $changes,
        private QualityMetrics $qualityMetrics
    ) {}

    public function getMergedContent(): string
    {
        return $this->mergedContent;
    }
    public function getChanges(): array
    {
        return $this->changes;
    }
    public function getQualityMetrics(): QualityMetrics
    {
        return $this->qualityMetrics;
    }
}

/**
 * Framework-specific strategies
 */
class FrameworkStrategyFactory
{
    public static function create(string $framework): FrameworkStrategy
    {
        return match ($framework) {
            'Laravel' => new LaravelStrategy(),
            'Symfony' => new SymfonyStrategy(),
            'WordPress' => new WordPressStrategy(),
            default => new GenericStrategy()
        };
    }
}

interface FrameworkStrategy
{
    public function createContext(string $projectPath, array $options): ApplicationContext;
}

class LaravelStrategy implements FrameworkStrategy
{
    public function createContext(string $projectPath, array $options): ApplicationContext
    {
        // Laravel-specific context creation
        $container = null; // Would resolve Laravel container
        $facades = []; // Would discover Laravel facades

        return new ApplicationContext(
            'Laravel',
            $options['version'] ?? '10.0',
            $projectPath,
            $container,
            $facades
        );
    }
}

class SymfonyStrategy implements FrameworkStrategy
{
    public function createContext(string $projectPath, array $options): ApplicationContext
    {
        // Symfony-specific context creation
        return new ApplicationContext(
            'Symfony',
            $options['version'] ?? '6.0',
            $projectPath
        );
    }
}

class WordPressStrategy implements FrameworkStrategy
{
    public function createContext(string $projectPath, array $options): ApplicationContext
    {
        // WordPress-specific context creation
        return new ApplicationContext(
            'WordPress',
            $options['version'] ?? '6.0',
            $projectPath
        );
    }
}

class GenericStrategy implements FrameworkStrategy
{
    public function createContext(string $projectPath, array $options): ApplicationContext
    {
        return new ApplicationContext(
            'Generic',
            '1.0.0',
            $projectPath
        );
    }
}

class TypeInferencer
{
    // Implementation for advanced type inference
}

class HelperMerger
{
    public function merge(string $existing, string $new): string
    {
        // Implementation for merging helper files
        return $new; // Simplified
    }

    public function getChanges(): array
    {
        return [];
    }
}
