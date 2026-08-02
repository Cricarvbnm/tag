# 共享库 — 由各 tag-* 命令 source
#
# 路径约定:
#   所有输入和输出路径均相对于 $PWD，或为绝对路径。
#   不假设 $PWD 等于 $TAG_ROOT。
#   用户传入的 tag 路径 (如 tag/type/text) 需真实存在于 $PWD 下。
#
# 输出约定:
#   查询类命令 (ls, tags, orphans, query) 空结果时静默退出 (exit 0)。
#   仅错误条件输出到 stderr 并 exit 1。

# 提供各种环境变量的默认值
if not set -q TAG_ROOT # 存放资源与标签的目录的位置
    set -g TAG_ROOT $PWD
end
if not set -q TAG_RES # 资源目录的名称
    set -g TAG_RES res
end
if not set -q TAG_DIR # 标签目录的名称
    set -g TAG_DIR tag
end
if not set -q TAG_LISTER # 展示文件时的 `ls`
    set -g TAG_LISTER "ls -1"
end

# 若当前 TAG_ROOT 下找不到 res/ 和 tag/，从 $PWD 向上搜索项目根目录
# 方便用户在子目录中操作，无需手动设置环境变量
if ! [ -d "$TAG_ROOT/$TAG_RES" ] || ! [ -d "$TAG_ROOT/$TAG_DIR" ]
    set -l dir $PWD
    set -g TAG_ROOT ""
    while [ "$dir" != / ]
        if [ -d "$dir/$TAG_RES" ] && [ -d "$dir/$TAG_DIR" ]
            set -g TAG_ROOT $dir
            break
        end
        set dir (dirname $dir)
    end
    # 遍历到根目录都没找到 — 保持 $PWD 作为兜底
    if [ -z "$TAG_ROOT" ]
        set -g TAG_ROOT $PWD
    end
end

# 输出报错信息并返回 1
function die
    echo $argv >&2
    return 1
end

# 将符号链接的目标解析为绝对路径 (不追踪目标中的符号链接)
function __reallink -a link
    set target (readlink $link)
    if string match -q '/*' -- $target
        realpath -s $target || return 1
    else
        set dir (realpath -s (dirname $link))
        realpath -s $dir/$target || return 1
    end
end

# 列出资源的标签目录中的链接，排序并去重
function __tag_links_of -a resource
    [ -e $resource ] || die "错误: 资源 $resource 不存在" || return 1

    set expected (realpath -s $resource)

    set result
    for link in (find $TAG_ROOT/$TAG_DIR -type l)
        set target (__reallink $link) || continue
        [ "$target" = "$expected" ] && set -a result (realpath -s --relative-base $PWD $link)
    end
    [ (count $result) -gt 0 ] && printf '%s\n' $result | sort -u
    return 0
end

# 列出标签的所有资源（目标路径），排序并去重
function __tag_resources_of -a tag
    [ -d $tag ] || die "错误: tag '$tag' 不存在" || return 1

    set result
    for link in (find $tag -type l)
        set target (__reallink $link) || continue
        set -a result (realpath -s --relative-base $PWD $target)
    end
    [ (count $result) -gt 0 ] && printf '%s\n' $result | sort -u
    return 0
end

# 展示目录项信息
function __list
    set -l cmd (string split ' ' -- $TAG_LISTER)
    $cmd -d $argv
end

# 树状展示
function __tree
    printf '%s\n' $argv | tree --fromfile .
end
