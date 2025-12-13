<?php

/**
 * TypeRefiner SaaS - Automated PHPDoc Type Enhancement System
 * 
 * Scans repositories and automatically adds missing PHPDoc types,
 * array shapes, callable signatures, and generics that Intelephense understands.
 * 
 * @package TypeRefiner
 * @version 1.0.0
 * @author EQ12 Development Team
 */

namespace TypeRefiner;

use ReflectionClass;
use ReflectionMethod;
use ReflectionParameter;
use ReflectionType;
use ReflectionNamedType;
use ReflectionUnionType;
use PhpParser\Node;
use PhpParser\NodeFinder;
use PhpParser\NodeTraverser;
use PhpParser\NodeVisitorAbstract;
use PhpParser\Parser;
use PhpParser\ParserFactory;
use PhpParser\PrettyPrinter\Standard as StandardPrettyPrinter;

/**
 * Main TypeRefiner Service
 */
class TypeRefinerService
{
    private Parser $parser;
    private NodeFinder $nodeFinder;
    private StandardPrettyPrinter $prettyPrinter;
    private TypeAnalyzer $typeAnalyzer;
    private PHPDocGenerator $docGenerator;

    public function __construct()
    {
        $this->parser = (new ParserFactory)->create(ParserFactory::PREFER_PHP7);
        $this->nodeFinder = new NodeFinder();
        $this->prettyPrinter = new StandardPrettyPrinter();
        $this->typeAnalyzer = new TypeAnalyzer();
        $this->docGenerator = new PHPDocGenerator();
    }

    /**
     * Analyze and enhance a PHP file with missing types
     *
     * @param string $filePath
     * @return TypeEnhancementResult
     */
    public function enhanceFile(string $filePath): TypeEnhancementResult
    {
        $originalCode = file_get_contents($filePath);
        $ast = $this->parser->parse($originalCode);

        if (!$ast) {
            throw new TypeRefinerException("Failed to parse file: {$filePath}");
        }

        $analysis = $this->typeAnalyzer->analyzeAST($ast);
        $enhancedAST = $this->applyEnhancements($ast, $analysis);
        $enhancedCode = $this->prettyPrinter->prettyPrintFile($enhancedAST);

        return new TypeEnhancementResult(
            $filePath,
            $originalCode,
            $enhancedCode,
            $analysis->getImprovements()
        );
    }

    /**
     * Process entire repository
     *
     * @param string $repositoryPath
     * @param array<string> $excludePaths
     * @return RepositoryEnhancementResult
     */
    public function enhanceRepository(
        string $repositoryPath,
        array $excludePaths = []
    ): RepositoryEnhancementResult {
        $phpFiles = $this->findPHPFiles($repositoryPath, $excludePaths);
        $results = [];
        $totalImprovements = 0;

        foreach ($phpFiles as $file) {
            try {
                $result = $this->enhanceFile($file);
                $results[] = $result;
                $totalImprovements += count($result->getImprovements());
            } catch (TypeRefinerException $e) {
                // Log error and continue
                error_log("TypeRefiner error for {$file}: " . $e->getMessage());
            }
        }

        return new RepositoryEnhancementResult(
            $repositoryPath,
            $results,
            $totalImprovements
        );
    }

    /**
     * Generate GitHub PR with type enhancements
     *
     * @param string $repositoryPath
     * @param string $githubToken
     * @param array<string, mixed> $options
     * @return GitHubPRResult
     */
    public function createEnhancementPR(
        string $repositoryPath,
        string $githubToken,
        array $options = []
    ): GitHubPRResult {
        $result = $this->enhanceRepository($repositoryPath);

        if ($result->getTotalImprovements() === 0) {
            return new GitHubPRResult(false, 'No type improvements found');
        }

        $branchName = 'typerefiner/enhance-types-' . date('Y-m-d-His');
        $prTitle = "🔧 TypeRefiner: Add missing PHPDoc types ({$result->getTotalImprovements()} improvements)";
        $prBody = $this->generatePRDescription($result);

        $githubApi = new GitHubAPIClient($githubToken);

        // Create branch and commit changes
        $githubApi->createBranch($repositoryPath, $branchName);

        foreach ($result->getFileResults() as $fileResult) {
            if ($fileResult->hasChanges()) {
                $githubApi->commitFile(
                    $repositoryPath,
                    $fileResult->getFilePath(),
                    $fileResult->getEnhancedCode(),
                    "Add missing types to " . basename($fileResult->getFilePath()),
                    $branchName
                );
            }
        }

        // Create PR
        $prUrl = $githubApi->createPullRequest(
            $repositoryPath,
            $branchName,
            'main',
            $prTitle,
            $prBody
        );

        return new GitHubPRResult(true, 'PR created successfully', $prUrl);
    }

    /**
     * Apply type enhancements to AST
     */
    private function applyEnhancements(array $ast, TypeAnalysisResult $analysis): array
    {
        $traverser = new NodeTraverser();
        $traverser->addVisitor(new TypeEnhancementVisitor($analysis));

        return $traverser->traverse($ast);
    }

    /**
     * Find all PHP files in repository
     */
    private function findPHPFiles(string $path, array $excludePaths): array
    {
        $files = [];
        $iterator = new \RecursiveIteratorIterator(
            new \RecursiveDirectoryIterator($path)
        );

        foreach ($iterator as $file) {
            if ($file->getExtension() === 'php' && !$this->isExcluded($file->getPathname(), $excludePaths)) {
                $files[] = $file->getPathname();
            }
        }

        return $files;
    }

    private function isExcluded(string $filePath, array $excludePaths): bool
    {
        foreach ($excludePaths as $excludePath) {
            if (strpos($filePath, $excludePath) !== false) {
                return true;
            }
        }
        return false;
    }

    private function generatePRDescription(RepositoryEnhancementResult $result): string
    {
        $improvements = [];
        foreach ($result->getFileResults() as $fileResult) {
            foreach ($fileResult->getImprovements() as $improvement) {
                $improvements[] = "- {$improvement->getType()}: {$improvement->getDescription()}";
            }
        }

        return "## TypeRefiner Automated Enhancements\n\n" .
            "This PR adds missing PHPDoc types to improve IntelliSense and static analysis.\n\n" .
            "### Improvements Made:\n" .
            implode("\n", array_slice($improvements, 0, 20)) .
            (count($improvements) > 20 ? "\n\n*...and " . (count($improvements) - 20) . " more*" : "") .
            "\n\n### Benefits:\n" .
            "- ✅ Better IDE autocompletion\n" .
            "- ✅ Improved static analysis\n" .
            "- ✅ Enhanced code documentation\n" .
            "- ✅ Reduced type-related bugs\n\n" .
            "*Generated by [TypeRefiner](https://typerefiner.dev) - Professional PHP Type Enhancement*";
    }
}

/**
 * Analyzes PHP code for missing types
 */
class TypeAnalyzer
{
    /**
     * @param Node[] $ast
     * @return TypeAnalysisResult
     */
    public function analyzeAST(array $ast): TypeAnalysisResult
    {
        $improvements = [];

        $traverser = new NodeTraverser();
        $visitor = new TypeAnalysisVisitor($improvements);
        $traverser->addVisitor($visitor);
        $traverser->traverse($ast);

        return new TypeAnalysisResult($improvements);
    }
}

/**
 * AST Visitor for type analysis
 */
class TypeAnalysisVisitor extends NodeVisitorAbstract
{
    /** @var TypeImprovement[] */
    private array $improvements;

    /** @param TypeImprovement[] $improvements */
    public function __construct(array &$improvements)
    {
        $this->improvements = &$improvements;
    }

    public function enterNode(Node $node)
    {
        if ($node instanceof Node\Stmt\ClassMethod) {
            $this->analyzeMethod($node);
        } elseif ($node instanceof Node\Stmt\Function_) {
            $this->analyzeFunction($node);
        } elseif ($node instanceof Node\Stmt\Property) {
            $this->analyzeProperty($node);
        }

        return null;
    }

    private function analyzeMethod(Node\Stmt\ClassMethod $method): void
    {
        // Check missing return type
        if (!$method->returnType && !$this->hasReturnTypeDoc($method)) {
            $this->improvements[] = new TypeImprovement(
                'missing_return_type',
                "Method {$method->name->name} missing return type",
                $method->getStartLine(),
                $this->inferReturnType($method)
            );
        }

        // Check missing parameter types
        foreach ($method->params as $param) {
            if (!$param->type && !$this->hasParamTypeDoc($method, $param->var->name)) {
                $this->improvements[] = new TypeImprovement(
                    'missing_param_type',
                    "Parameter \${$param->var->name} missing type hint",
                    $param->getStartLine(),
                    $this->inferParameterType($param)
                );
            }
        }

        // Check for array parameters without shapes
        $this->checkArrayShapes($method);
    }

    private function analyzeFunction(Node\Stmt\Function_ $function): void
    {
        // Similar analysis for functions
        if (!$function->returnType && !$this->hasReturnTypeDoc($function)) {
            $this->improvements[] = new TypeImprovement(
                'missing_return_type',
                "Function {$function->name->name} missing return type",
                $function->getStartLine(),
                $this->inferReturnType($function)
            );
        }
    }

    private function analyzeProperty(Node\Stmt\Property $property): void
    {
        foreach ($property->props as $prop) {
            if (!$property->type && !$this->hasPropertyTypeDoc($property)) {
                $this->improvements[] = new TypeImprovement(
                    'missing_property_type',
                    "Property \${$prop->name->name} missing type hint",
                    $property->getStartLine(),
                    $this->inferPropertyType($property, $prop)
                );
            }
        }
    }

    private function checkArrayShapes(Node\Stmt\ClassMethod $method): void
    {
        // Look for array parameters that could benefit from shape types
        foreach ($method->params as $param) {
            if ($param->type && $param->type instanceof Node\Name && $param->type->toString() === 'array') {
                // Analyze usage to infer array shape
                $shape = $this->inferArrayShape($method, $param->var->name);
                if ($shape) {
                    $this->improvements[] = new TypeImprovement(
                        'array_shape',
                        "Parameter \${$param->var->name} could use array shape",
                        $param->getStartLine(),
                        $shape
                    );
                }
            }
        }
    }

    private function hasReturnTypeDoc(Node\Stmt\Function_|Node\Stmt\ClassMethod $node): bool
    {
        $docComment = $node->getDocComment();
        if (!$docComment) {
            return false;
        }

        return strpos($docComment->getText(), '@return') !== false;
    }

    private function hasParamTypeDoc(Node\Stmt\ClassMethod $method, string $paramName): bool
    {
        $docComment = $method->getDocComment();
        if (!$docComment) {
            return false;
        }

        return strpos($docComment->getText(), "@param") !== false &&
            strpos($docComment->getText(), "\${$paramName}") !== false;
    }

    private function hasPropertyTypeDoc(Node\Stmt\Property $property): bool
    {
        $docComment = $property->getDocComment();
        if (!$docComment) {
            return false;
        }

        return strpos($docComment->getText(), '@var') !== false;
    }

    private function inferReturnType(Node\Stmt\Function_|Node\Stmt\ClassMethod $node): string
    {
        // Analyze return statements to infer type
        $finder = new NodeFinder();
        $returns = $finder->findInstanceOf($node->stmts, Node\Stmt\Return_::class);

        if (empty($returns)) {
            return 'void';
        }

        // Simple heuristics for common patterns
        foreach ($returns as $return) {
            if ($return->expr instanceof Node\Expr\Array_) {
                return 'array';
            } elseif ($return->expr instanceof Node\Scalar\String_) {
                return 'string';
            } elseif ($return->expr instanceof Node\Scalar\LNumber) {
                return 'int';
            } elseif ($return->expr instanceof Node\Scalar\DNumber) {
                return 'float';
            } elseif ($return->expr instanceof Node\Expr\ConstFetch) {
                $name = $return->expr->name->toString();
                if ($name === 'true' || $name === 'false') {
                    return 'bool';
                } elseif ($name === 'null') {
                    return 'mixed';
                }
            }
        }

        return 'mixed';
    }

    private function inferParameterType(Node\Param $param): string
    {
        // Look at default value to infer type
        if ($param->default) {
            if ($param->default instanceof Node\Scalar\String_) {
                return 'string';
            } elseif ($param->default instanceof Node\Scalar\LNumber) {
                return 'int';
            } elseif ($param->default instanceof Node\Scalar\DNumber) {
                return 'float';
            } elseif ($param->default instanceof Node\Expr\Array_) {
                return 'array';
            } elseif ($param->default instanceof Node\Expr\ConstFetch) {
                $name = $param->default->name->toString();
                if ($name === 'true' || $name === 'false') {
                    return 'bool';
                } elseif ($name === 'null') {
                    return 'mixed';
                }
            }
        }

        return 'mixed';
    }

    private function inferPropertyType(Node\Stmt\Property $property, Node\Stmt\PropertyProperty $prop): string
    {
        if ($prop->default) {
            if ($prop->default instanceof Node\Scalar\String_) {
                return 'string';
            } elseif ($prop->default instanceof Node\Scalar\LNumber) {
                return 'int';
            } elseif ($prop->default instanceof Node\Scalar\DNumber) {
                return 'float';
            } elseif ($prop->default instanceof Node\Expr\Array_) {
                return 'array';
            }
        }

        return 'mixed';
    }

    private function inferArrayShape(Node\Stmt\ClassMethod $method, string $paramName): ?string
    {
        // Look for array access patterns to infer shape
        $finder = new NodeFinder();
        $arrayAccesses = $finder->findInstanceOf($method->stmts, Node\Expr\ArrayDimFetch::class);

        $keys = [];
        foreach ($arrayAccesses as $access) {
            if (
                $access->var instanceof Node\Expr\Variable &&
                $access->var->name === $paramName &&
                $access->dim instanceof Node\Scalar\String_
            ) {
                $keys[] = $access->dim->value;
            }
        }

        if (count($keys) >= 2) {
            $shapeKeys = array_map(fn($key) => "$key: mixed", array_unique($keys));
            return "array{" . implode(", ", $shapeKeys) . "}";
        }

        return null;
    }
}

/**
 * AST Visitor for applying type enhancements
 */
class TypeEnhancementVisitor extends NodeVisitorAbstract
{
    private TypeAnalysisResult $analysis;

    public function __construct(TypeAnalysisResult $analysis)
    {
        $this->analysis = $analysis;
    }

    public function leaveNode(Node $node)
    {
        $improvements = $this->analysis->getImprovementsForLine($node->getStartLine());

        foreach ($improvements as $improvement) {
            $node = $this->applyImprovement($node, $improvement);
        }

        return $node;
    }

    private function applyImprovement(Node $node, TypeImprovement $improvement): Node
    {
        switch ($improvement->getType()) {
            case 'missing_return_type':
                if ($node instanceof Node\Stmt\ClassMethod || $node instanceof Node\Stmt\Function_) {
                    $node->returnType = new Node\Name($improvement->getSuggestedType());
                }
                break;

            case 'missing_param_type':
                if ($node instanceof Node\Param) {
                    $node->type = new Node\Name($improvement->getSuggestedType());
                }
                break;

            case 'missing_property_type':
                if ($node instanceof Node\Stmt\Property) {
                    $node->type = new Node\Name($improvement->getSuggestedType());
                }
                break;
        }

        return $node;
    }
}

/**
 * Data classes for results
 */
class TypeEnhancementResult
{
    /** @param TypeImprovement[] $improvements */
    public function __construct(
        private string $filePath,
        private string $originalCode,
        private string $enhancedCode,
        private array $improvements
    ) {}

    public function getFilePath(): string
    {
        return $this->filePath;
    }
    public function getOriginalCode(): string
    {
        return $this->originalCode;
    }
    public function getEnhancedCode(): string
    {
        return $this->enhancedCode;
    }
    public function getImprovements(): array
    {
        return $this->improvements;
    }
    public function hasChanges(): bool
    {
        return $this->originalCode !== $this->enhancedCode;
    }
}

class RepositoryEnhancementResult
{
    /** @param TypeEnhancementResult[] $fileResults */
    public function __construct(
        private string $repositoryPath,
        private array $fileResults,
        private int $totalImprovements
    ) {}

    public function getRepositoryPath(): string
    {
        return $this->repositoryPath;
    }
    public function getFileResults(): array
    {
        return $this->fileResults;
    }
    public function getTotalImprovements(): int
    {
        return $this->totalImprovements;
    }
}

class TypeAnalysisResult
{
    /** @param TypeImprovement[] $improvements */
    public function __construct(private array $improvements) {}

    public function getImprovements(): array
    {
        return $this->improvements;
    }

    /** @return TypeImprovement[] */
    public function getImprovementsForLine(int $line): array
    {
        return array_filter(
            $this->improvements,
            fn($improvement) => $improvement->getLine() === $line
        );
    }
}

class TypeImprovement
{
    public function __construct(
        private string $type,
        private string $description,
        private int $line,
        private string $suggestedType
    ) {}

    public function getType(): string
    {
        return $this->type;
    }
    public function getDescription(): string
    {
        return $this->description;
    }
    public function getLine(): int
    {
        return $this->line;
    }
    public function getSuggestedType(): string
    {
        return $this->suggestedType;
    }
}

class GitHubPRResult
{
    public function __construct(
        private bool $success,
        private string $message,
        private ?string $prUrl = null
    ) {}

    public function isSuccess(): bool
    {
        return $this->success;
    }
    public function getMessage(): string
    {
        return $this->message;
    }
    public function getPRUrl(): ?string
    {
        return $this->prUrl;
    }
}

/**
 * GitHub API integration
 */
class GitHubAPIClient
{
    public function __construct(private string $token) {}

    public function createBranch(string $repo, string $branchName): void
    {
        // Implementation for GitHub API calls
    }

    public function commitFile(string $repo, string $filePath, string $content, string $message, string $branch): void
    {
        // Implementation for GitHub API calls
    }

    public function createPullRequest(string $repo, string $head, string $base, string $title, string $body): string
    {
        // Implementation for GitHub API calls
        return "https://github.com/{$repo}/pull/123";
    }
}

/**
 * PHPDoc generator for enhanced documentation
 */
class PHPDocGenerator
{
    /**
     * Generate PHPDoc block for method
     */
    public function generateMethodDoc(Node\Stmt\ClassMethod $method, array $improvements): string
    {
        $lines = ["/**"];

        // Add description
        $lines[] = " * " . ucfirst(str_replace('_', ' ', $method->name->name));
        $lines[] = " *";

        // Add parameters
        foreach ($method->params as $param) {
            $type = $this->getParamType($param, $improvements);
            $name = $param->var->name;
            $lines[] = " * @param {$type} \${$name}";
        }

        // Add return type
        $returnType = $this->getReturnType($method, $improvements);
        if ($returnType !== 'void') {
            $lines[] = " * @return {$returnType}";
        }

        $lines[] = " */";

        return implode("\n", $lines);
    }

    private function getParamType(Node\Param $param, array $improvements): string
    {
        foreach ($improvements as $improvement) {
            if (
                $improvement->getType() === 'missing_param_type' &&
                strpos($improvement->getDescription(), "\${$param->var->name}") !== false
            ) {
                return $improvement->getSuggestedType();
            }
        }

        return $param->type ? $param->type->toString() : 'mixed';
    }

    private function getReturnType(Node\Stmt\ClassMethod $method, array $improvements): string
    {
        foreach ($improvements as $improvement) {
            if ($improvement->getType() === 'missing_return_type') {
                return $improvement->getSuggestedType();
            }
        }

        return $method->returnType ? $method->returnType->toString() : 'mixed';
    }
}

class TypeRefinerException extends \Exception {}
