import 'dart:io';
import 'package:analyzer/dart/analysis/analysis_context_collection.dart';
import 'package:analyzer/dart/analysis/results.dart';
import 'package:analyzer/dart/element/element.dart';

void main(List<String> args) async {
  if (args.length != 1) {
    throw ArgumentError(
      'Exactly 1 argument required. Usage: dart run list_symbols.dart <entrypoint_file.dart>',
    );
  }

  final entrypointFile = File(args.single).absolute;
  if (!entrypointFile.existsSync()) {
    throw FileSystemException(
        'Entrypoint file does not exist', entrypointFile.path);
  }

  final entrypoint = entrypointFile.path;
  final collection = AnalysisContextCollection(includedPaths: [entrypoint]);
  final context = collection.contextFor(entrypoint);
  final session = context.currentSession;

  final result = await session.getResolvedLibrary(entrypoint);
  if (result is! ResolvedLibraryResult) {
    throw StateError('Failed to resolve library at $entrypoint');
  }

  final exported = result.element.exportNamespace.definedNames2;
  print('Total exported top-level symbols: ${exported.length}\n');

  final sortedEntries = exported.entries.toList()
    ..sort((a, b) => a.key.compareTo(b.key));

  for (final entry in sortedEntries) {
    final dynamic elem = entry.value;
    print('[${elem.kind.displayName.toUpperCase()}] ${entry.key}');
    if (elem is Element) {
      _printPublicMembers(elem);
    }
  }
}

void _printPublicMembers(Element element) {
  if (element is InterfaceElement) {
    // 1. Constructors
    final constructors =
        element.constructors.where((c) => !c.isPrivate).map((c) {
      final cName = c.name;
      return (cName == null || cName.isEmpty || cName == 'new')
          ? '${element.name}()'
          : '${element.name}.$cName()';
    }).toList()
          ..sort();
    if (constructors.isNotEmpty) {
      print('  Constructors:');
      for (final c in constructors) {
        print('    - $c');
      }
    }

    // 2. Enum values (if Enum)
    if (element is EnumElement) {
      final values = element.fields
          .where((f) => f.isEnumConstant && !f.isPrivate)
          .map((f) => f.name)
          .whereType<String>()
          .toList()
        ..sort();
      if (values.isNotEmpty) {
        print('  Values:');
        for (final v in values) {
          print('    - $v');
        }
      }
    }

    // 3. Fields / Properties
    final fields = element.fields
        .where((f) => !f.isPrivate && !f.isEnumConstant)
        .map((f) => '${f.isStatic ? "static " : ""}${f.name}')
        .toList()
      ..sort();
    if (fields.isNotEmpty) {
      print('  Fields:');
      for (final f in fields) {
        print('    - $f');
      }
    }

    // 4. Methods
    final methods = element.methods
        .where((m) => !m.isPrivate)
        .map((m) => '${m.isStatic ? "static " : ""}${m.name}()')
        .toList()
      ..sort();
    if (methods.isNotEmpty) {
      print('  Methods:');
      for (final m in methods) {
        print('    - $m');
      }
    }
  } else if (element is ExtensionElement) {
    // Methods and fields for extensions
    final methods = element.methods
        .where((m) => !m.isPrivate)
        .map((m) => '${m.isStatic ? "static " : ""}${m.name}()')
        .toList()
      ..sort();
    if (methods.isNotEmpty) {
      print('  Extension Methods:');
      for (final m in methods) {
        print('    - $m');
      }
    }
  }
}
